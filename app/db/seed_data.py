import json
import os
from datetime import date
from typing import Dict, Any
from sqlalchemy.orm import Session

from .db_config import SessionLocal, engine
from .models import (
    Base, Supplier, Category, SupplierCategory, SupplierLocation,
    Contact, OrderCondition, Certificate, UserNote
)

DATA_PATH = 'data.json'
def load_json_data() -> Dict[str, Any]:
    """Загрузить данные из JSON файла."""
    json_path = os.path.join(os.path.dirname(__file__), DATA_PATH)
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def clear_tables(db: Session) -> None:
    """Очистить все таблицы в правильном порядке (с учетом внешних ключей)."""
    # Удаляем в порядке от зависимых к основным
    db.query(UserNote).delete()
    db.query(Certificate).delete()
    db.query(OrderCondition).delete()
    db.query(Contact).delete()
    db.query(SupplierLocation).delete()
    db.query(SupplierCategory).delete()
    db.query(Supplier).delete()
    db.query(Category).delete()
    db.commit()


def get_or_create_category(db: Session, category_data: Dict[str, Any]) -> Category:
    """Получить категорию по названию или создать новую."""
    name = category_data['name']
    existing = db.query(Category).filter(Category.name == name).first()
    if existing:
        return existing
    
    # Создаем новую категорию
    category = Category(
        name=name,
        description=category_data.get('description', ''),
        parent_id=category_data.get('parent_id')  # Может быть None
    )
    db.add(category)
    db.flush()  # Получаем ID, но не коммитим
    return category


def create_supplier_from_json(db: Session, supplier_data: Dict[str, Any]) -> Supplier:
    """Создать поставщика из JSON данных."""
    # 1. Создаем поставщика
    supplier = Supplier(
        name=supplier_data['name'],
        description=supplier_data.get('description', ''),
        city=supplier_data.get('city'),
        region=supplier_data.get('region'),
        address=supplier_data.get('address', ''),
        website=supplier_data.get('website', ''),
        foundation_year=supplier_data.get('foundation_year'),
        rating=supplier_data.get('rating', 0),
        rating_count=supplier_data.get('rating_count', 0),
        is_verified=supplier_data.get('is_verified', False),
        status=supplier_data.get('status', 'active')
    )
    db.add(supplier)
    db.flush()  # Получаем ID поставщика

    # 1b. Создаем локации
    locations_data = supplier_data.get('locations')
    if locations_data and isinstance(locations_data, list):
        for loc in locations_data:
            if loc.get('city'):
                db.add(SupplierLocation(
                    supplier_id=supplier.id,
                    city=loc['city'],
                    region=loc.get('region'),
                ))
    elif supplier.city:
        db.add(SupplierLocation(
            supplier_id=supplier.id,
            city=supplier.city,
            region=supplier.region,
        ))

    # 2. Добавляем категории
    categories = supplier_data.get('categories', [])
    for cat_data in categories:
        # Ищем категорию по названию
        category = db.query(Category).filter(Category.name == cat_data['name']).first()
        if category:
            supplier_category = SupplierCategory(
                supplier_id=supplier.id,
                category_id=category.id,
                is_main=cat_data.get('is_main', False)
            )
            db.add(supplier_category)
    
    # 3. Добавляем контакты
    contacts = supplier_data.get('contacts', [])
    for contact_data in contacts:
        contact = Contact(
            supplier_id=supplier.id,
            contact_type=contact_data['type'],
            contact_value=contact_data['value'],
            contact_person=contact_data.get('contact_person'),
            is_primary=contact_data.get('is_primary', False)
        )
        db.add(contact)
    
    # 4. Добавляем условия заказа
    order_conditions = supplier_data.get('order_conditions', [])
    for oc_data in order_conditions:
        # Находим категорию по имени
        category = db.query(Category).filter(Category.name == oc_data['category_name']).first()
        
        order_condition = OrderCondition(
            supplier_id=supplier.id,
            category_id=category.id if category else None,
            min_order_quantity=oc_data.get('min_order_quantity'),
            min_order_unit=oc_data.get('min_order_unit'),
            price_per_unit=oc_data.get('price_per_unit'),
            price_currency=oc_data.get('price_currency', 'RUB'),
            price_negotiable=oc_data.get('price_negotiable', True),
            delivery_terms=oc_data.get('delivery_terms', ''),
            delivery_region=oc_data.get('delivery_region', ''),
            delivery_cost=oc_data.get('delivery_cost'),
            payment_terms=oc_data.get('payment_terms', ''),
            lead_time_days=oc_data.get('lead_time_days')
        )
        db.add(order_condition)
    
    # 5. Добавляем сертификаты
    certificates = supplier_data.get('certificates', [])
    for cert_data in certificates:
        issued_date = None
        expiry_date = None
        
        if cert_data.get('issued_date'):
            issued_date = date.fromisoformat(cert_data['issued_date'])
        if cert_data.get('expiry_date'):
            expiry_date = date.fromisoformat(cert_data['expiry_date'])
        
        certificate = Certificate(
            supplier_id=supplier.id,
            certificate_name=cert_data['certificate_name'],
            certificate_type=cert_data.get('certificate_type'),
            issuing_authority=cert_data.get('issuing_authority'),
            issued_date=issued_date,
            expiry_date=expiry_date,
            file_url=cert_data.get('file_url'),
            is_valid=cert_data.get('is_valid', True)
        )
        db.add(certificate)
    
    # 6. Добавляем заметки
    notes = supplier_data.get('notes', [])
    for note_data in notes:
        note = UserNote(
            supplier_id=supplier.id,
            note_text=note_data['note_text'],
            note_type=note_data.get('note_type', 'general'),
            rating_impact=note_data.get('rating_impact', 0)
        )
        db.add(note)
    
    return supplier


def seed_database() -> None:
    """Заполнить БД тестовыми данными из JSON."""
    db = SessionLocal()
    
    try:
        print("📖 Загрузка данных из JSON...")
        data = load_json_data()
        
        print("📝 Создание таблиц...")
        Base.metadata.create_all(engine)

        print("🗑️  Очистка таблиц...")
        clear_tables(db)
        
        print("📂 Импорт категорий...")
        # Сначала создаем все категории
        categories_data = data.get('categories', [])
        category_map = {}  # name -> id
        
        for cat_data in categories_data:
            category = Category(
                name=cat_data['name'],
                description=cat_data.get('description', ''),
                parent_id=None  # Пока оставляем None
            )
            db.add(category)
            db.flush()
            category_map[cat_data['name']] = category.id
        
        # Обновляем parent_id для категорий
        for cat_data in categories_data:
            if cat_data.get('parent_id') is not None:
                # parent_id в JSON это индекс (1-based) или null
                parent_index = cat_data['parent_id'] - 1  # 0-based
                if 0 <= parent_index < len(categories_data):
                    parent_name = categories_data[parent_index]['name']
                    parent_id = category_map.get(parent_name)
                    
                    if parent_id:
                        db.query(Category).filter(
                            Category.name == cat_data['name']
                        ).update({"parent_id": parent_id})
        
        db.flush()
        
        print(f"   ✅ Создано {len(categories_data)} категорий")
        
        print("📦 Импорт поставщиков...")
        suppliers_data = data.get('suppliers', [])
        
        for supplier_data in suppliers_data:
            try:
                create_supplier_from_json(db, supplier_data)
            except Exception as e:
                print(f"   ❌ Ошибка при создании поставщика {supplier_data.get('name', 'Unknown')}: {e}")
                continue
        
        db.commit()
        
        # Статистика
        supplier_count = db.query(Supplier).count()
        category_count = db.query(Category).count()
        contact_count = db.query(Contact).count()
        cert_count = db.query(Certificate).count()
        note_count = db.query(UserNote).count()
        
        print("\n✅ База данных успешно заполнена!")
        print(f"   📊 Статистика:")
        print(f"   - Поставщиков: {supplier_count}")
        print(f"   - Категорий: {category_count}")
        print(f"   - Контактов: {contact_count}")
        print(f"   - Сертификатов: {cert_count}")
        print(f"   - Заметок: {note_count}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при заполнении БД: {e}")
        raise
    finally:
        db.close()


def update_certificate_validity(db: Session) -> None:
    """Обновить статус валидности сертификатов (опционально)."""
    from datetime import date
    today = date.today()
    
    updated = db.query(Certificate).filter(
        Certificate.expiry_date < today,
        Certificate.is_valid == True
    ).update({"is_valid": False})
    
    db.commit()
    if updated > 0:
        print(f"   ✅ Обновлено {updated} сертификатов (просрочены)")


if __name__ == "__main__":
    print("🚀 Запуск заполнения БД...")
    seed_database()
