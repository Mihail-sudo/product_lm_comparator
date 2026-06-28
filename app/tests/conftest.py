from typing import Generator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.models import (
    Base, Supplier, Category, SupplierCategory, Contact,
    Certificate,
)
from app.db.db_config import get_db
from app.backend.main import app


TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def seed_test_data(db: Session):
    cat_root = Category(name="Сырье", description="Сырье для производства")
    cat_child = Category(name="Мука", description="Мука пшеничная")
    cat_other = Category(name="Упаковка", description="Упаковочные материалы")
    db.add_all([cat_root, cat_child, cat_other])
    db.flush()

    cat_child.parent_id = cat_root.id
    db.flush()

    supplier = Supplier(
        name="ООО Поставщик",
        description="Крупный поставщик сырья",
        city="Москва",
        region="Центральный",
        address="ул. Ленина, 1",
        website="https://supplier.ru",
        foundation_year=2010,
        rating=4.5,
        rating_count=10,
        is_verified=True,
        status="active",
    )
    db.add(supplier)
    db.flush()

    db.add(SupplierCategory(supplier_id=supplier.id, category_id=cat_root.id, is_main=True))
    db.add(SupplierCategory(supplier_id=supplier.id, category_id=cat_child.id, is_main=False))

    db.add(Contact(
        supplier_id=supplier.id,
        contact_type="phone",
        contact_value="+7-495-123-45-67",
        contact_person="Иван Иванов",
        is_primary=True,
    ))

    db.add(Certificate(
        supplier_id=supplier.id,
        certificate_name="ISO 9001",
        certificate_type="iso",
        issuing_authority="Росстандарт",
        issued_date=date(2023, 1, 1),
        expiry_date=date(2026, 1, 1),
        is_valid=True,
    ))

    supplier2 = Supplier(
        name="ИП Производитель",
        description="Мелкий производитель",
        city="Казань",
        region="Приволжский",
        address="ул. Баумана, 10",
        rating=3.0,
        rating_count=5,
        is_verified=False,
        status="active",
    )
    db.add(supplier2)
    db.flush()

    db.add(SupplierCategory(supplier_id=supplier2.id, category_id=cat_child.id, is_main=True))

    supplier3 = Supplier(
        name="ООО Тест",
        description="Неактивный поставщик",
        city="Москва",
        region="Центральный",
        rating=0,
        rating_count=0,
        is_verified=False,
        status="inactive",
    )
    db.add(supplier3)

    db.commit()


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_test_data(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)
