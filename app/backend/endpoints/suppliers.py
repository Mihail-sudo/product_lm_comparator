from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.crud import suppliers as crud
from app.schemas.supplier import (
    SupplierResponse, SupplierCreate, SupplierUpdate,
    SupplierListResponse, ParseFromUrlRequest,
)
from app.db.db_config import get_db
from app.db.models import Supplier, Category, SupplierCategory, SupplierLocation, Contact, Certificate, OrderCondition
from app.backend.services.url_parser import parse_supplier_from_url
from app.backend.services.llm_client import DEFAULT_MODEL

from .serializer import serialize_supplier

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("/", response_model=SupplierListResponse)
def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    only_active: bool = True,
    db: Session = Depends(get_db)
):
    """Получить список всех поставщиков с пагинацией."""
    total = crud.get_suppliers_count(db, only_active=only_active)
    items = crud.get_all_suppliers(db, skip=skip, limit=limit, only_active=only_active)

    response_items = []
    for supplier in items:
        # Создаем словарь с данными поставщика
        response_items.append(serialize_supplier(supplier))
    
    return SupplierListResponse(
        total=total, 
        items=response_items, 
        skip=skip, 
        limit=limit
    )


@router.get("/search", response_model=SupplierListResponse)
def search_suppliers(
    query_text: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    has_certificates: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    min_order_max: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Расширенный поиск поставщиков."""
    items = crud.search_suppliers(
        db=db,
        query_text=query_text,
        category_id=category_id,
        city=city,
        region=region,
        min_rating=min_rating,
        has_certificates=has_certificates,
        is_verified=is_verified,
        min_order_max=min_order_max,
        skip=skip,
        limit=limit
    )

    total = crud.search_suppliers_count(
        db=db,
        query_text=query_text,
        category_id=category_id,
        city=city,
        region=region,
        min_rating=min_rating,
        has_certificates=has_certificates,
        is_verified=is_verified,
        min_order_max=min_order_max,
    )

    response_items = []
    for supplier in items:
        response_items.append(serialize_supplier(supplier))

    return SupplierListResponse(total=total, items=response_items, skip=skip, limit=limit)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Получить поставщика по ID."""
    supplier = crud.get_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return serialize_supplier(supplier)


@router.post("/", response_model=SupplierResponse, status_code=201)
def create_supplier(supplier_data: SupplierCreate, db: Session = Depends(get_db)):
    """Создать нового поставщика."""
    new_supplier = crud.create_supplier(db, supplier_data.model_dump())
    new_supplier = serialize_supplier(new_supplier)
    return new_supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, supplier_data: SupplierUpdate, db: Session = Depends(get_db)):
    """Обновить данные поставщика."""
    supplier = crud.update_supplier(db, supplier_id, supplier_data.model_dump(exclude_unset=True))
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.refresh(supplier)
    return serialize_supplier(supplier)


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Удалить поставщика."""
    deleted = crud.delete_supplier(db, supplier_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return None


@router.post("/{supplier_id}/rating/update", response_model=SupplierResponse)
def update_rating(supplier_id: int, db: Session = Depends(get_db)):
    """Пересчитать рейтинг поставщика на основе заметок."""
    supplier = crud.get_supplier(db, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    crud.update_supplier_rating(db, supplier_id)
    db.refresh(supplier)
    return serialize_supplier(supplier)


@router.post("/parse-from-url", response_model=SupplierResponse, status_code=201)
def parse_supplier_from_url_endpoint(
    request: ParseFromUrlRequest,
    db: Session = Depends(get_db),
):
    """Распарсить сайт поставщика по URL и создать запись в БД."""
    all_categories = db.query(Category).order_by(Category.name).all()
    all_category_names = [c.name for c in all_categories]
    parent_to_children: dict[str, list[str]] = {}
    parent_category_names: set[str] = set()
    for c in all_categories:
        if c.parent_id is None:
            parent_category_names.add(c.name)
            parent_to_children[c.name] = []
        else:
            parent_name = next(
                (p.name for p in all_categories if p.id == c.parent_id), None
            )
            if parent_name:
                parent_to_children.setdefault(parent_name, []).append(c.name)

    parsed = parse_supplier_from_url(
        request.url,
        model=request.model or DEFAULT_MODEL,
        existing_categories=all_category_names,
    )
    if not parsed:
        raise HTTPException(
            status_code=422,
            detail="Не удалось распарсить данные с указанного URL",
        )

    categories_from_site = parsed.pop("categories", [])
    categories_from_site = [
        c for c in categories_from_site
        if isinstance(c, str) and c.strip()
    ]
    expanded = []
    for c in categories_from_site:
        if c in parent_category_names:
            expanded.extend(parent_to_children.get(c, []))
        else:
            expanded.append(c)
    all_leaf_names = set(all_category_names) - parent_category_names
    skipped_cats = [c for c in expanded if c not in all_leaf_names]
    if skipped_cats:
        print(f"Предупреждение: категории {skipped_cats} не найдены в БД или являются родительскими", flush=True)
    categories_from_site = list({c for c in expanded if c in all_leaf_names})

    if not categories_from_site:
        raise HTTPException(
            status_code=422,
            detail="Не удалось определить категории поставщика — сайт не добавлен",
        )

    contacts_from_site = parsed.pop("contacts", []) or []
    certificates_from_site = parsed.pop("certificates", []) or []
    order_conditions_from_site = parsed.pop("order_conditions", []) or []

    supplier_fields = {
        k: parsed[k]
        for k in ("name", "description", "city", "region", "address",
                  "website", "foundation_year", "is_verified", "status")
        if k in parsed and parsed[k] is not None
    }

    if not supplier_fields.get("name"):
        raise HTTPException(status_code=422, detail="Не удалось определить название компании")

    if not supplier_fields.get("city"):
        supplier_fields["city"] = "Не указан"

    locations_from_site = parsed.pop("locations", None)
    has_locations_from_site = bool(locations_from_site and isinstance(locations_from_site, list))

    supplier = Supplier(**supplier_fields)
    db.add(supplier)
    db.flush()

    if has_locations_from_site:
        for loc in locations_from_site:
            if loc.get("city"):
                db.add(SupplierLocation(
                    supplier_id=supplier.id,
                    city=loc["city"],
                    region=loc.get("region"),
                ))
    elif supplier.city and supplier.city != "Не указан":
        db.add(SupplierLocation(
            supplier_id=supplier.id,
            city=supplier.city,
            region=supplier.region,
        ))

    VALID_CONTACT_TYPES = {"phone", "email", "telegram", "whatsapp", "viber", "other"}
    VALID_CERT_TYPES = {"quality", "safety", "organic", "halal", "kosher", "iso", "other"}

    for cat_name in categories_from_site:
        if not cat_name or not isinstance(cat_name, str):
            continue
        category = db.query(Category).filter(Category.name == cat_name).first()
        if category:
            link = SupplierCategory(supplier_id=supplier.id, category_id=category.id, is_main=False)
            db.add(link)

    for c in contacts_from_site:
        if not c.get("value"):
            continue
        ctype = c.get("type", "other")
        if ctype not in VALID_CONTACT_TYPES:
            ctype = "other"
        contact = Contact(
            supplier_id=supplier.id,
            contact_type=ctype,
            contact_value=c["value"],
            contact_person=c.get("contact_person"),
            is_primary=c.get("is_primary", False),
        )
        db.add(contact)

    for c in certificates_from_site:
        if not c.get("certificate_name"):
            continue
        ctype = c.get("certificate_type", "other")
        if ctype not in VALID_CERT_TYPES:
            ctype = "other"
        cert = Certificate(
            supplier_id=supplier.id,
            certificate_name=c["certificate_name"],
            certificate_type=ctype,
            issuing_authority=c.get("issuing_authority"),
            issued_date=c.get("issued_date"),
            expiry_date=c.get("expiry_date"),
            is_valid=c.get("is_valid", True),
        )
        db.add(cert)

    VALID_ORDER_UNITS = {"kg", "ton", "piece", "box", "pallet", "liter", "other"}
    for oc in order_conditions_from_site:
        if not oc.get("category_name"):
            continue
        cat = db.query(Category).filter(Category.name == oc["category_name"]).first()
        unit = oc.get("min_order_unit", "other")
        if unit not in VALID_ORDER_UNITS:
            unit = "other"
        order_condition = OrderCondition(
            supplier_id=supplier.id,
            category_id=cat.id if cat else None,
            min_order_quantity=oc.get("min_order_quantity"),
            min_order_unit=unit,
            price_per_unit=oc.get("price_per_unit"),
            price_currency=oc.get("price_currency", "RUB"),
            price_negotiable=oc.get("price_negotiable", True),
            delivery_terms=oc.get("delivery_terms"),
            delivery_region=oc.get("delivery_region"),
            delivery_cost=oc.get("delivery_cost"),
            payment_terms=oc.get("payment_terms"),
            lead_time_days=oc.get("lead_time_days"),
        )
        db.add(order_condition)

    db.commit()
    db.refresh(supplier)
    return serialize_supplier(supplier)
