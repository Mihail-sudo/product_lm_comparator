def serialize_supplier(supplier) -> dict:
    """Сериализует Supplier объект для Pydantic валидации."""
    return {
        "id": supplier.id,
        "name": supplier.name,
        "description": supplier.description,
        "city": supplier.city,
        "region": supplier.region,
        "address": supplier.address,
        "website": supplier.website,
        "foundation_year": supplier.foundation_year,
        "is_verified": supplier.is_verified,
        "status": supplier.status,
        "rating": supplier.rating,
        "rating_count": supplier.rating_count,
        "created_at": supplier.created_at,
        "updated_at": supplier.updated_at,
        "categories": [
            {
                "id": sc.category.id,
                "name": sc.category.name,
                "description": getattr(sc.category, 'description', None),
                "created_at": sc.category.created_at,
            }
            for sc in (supplier.categories or [])
        ],
        "contacts": [
            {
                "id": contact.id,
                "contact_type": contact.contact_type,
                "contact_value": contact.contact_value,
                "supplier_id": supplier.id,
                "is_primary": contact.is_primary,
                "created_at": contact.created_at,
                "contact_person": contact.contact_person
            }
            for contact in (supplier.contacts or [])
        ],
    }


def serialize_2_compare(supplier) -> dict:
    """Сериализует Supplier объект для Pydantic валидации."""
    return {
        "id": supplier.id,
        "name": supplier.name,
        "description": supplier.description,
        "city": supplier.city,
        "region": supplier.region,
        "address": supplier.address,
        "website": supplier.website,
        "foundation_year": supplier.foundation_year,
        "is_verified": supplier.is_verified,
        "status": supplier.status,
        "rating": supplier.rating,
        "rating_count": supplier.rating_count,
        "created_at": supplier.created_at,
        "updated_at": supplier.updated_at,
        "categories": [
            sc.category for sc in (supplier.categories or [])
        ],
        "contacts": [
            contact for contact in (supplier.contacts or [])
        ],
        "certificates": [
            certificate for certificate in (supplier.certificates or [])
        ],
        "notes": [
            note for note in (supplier.notes or [])
        ]
    }