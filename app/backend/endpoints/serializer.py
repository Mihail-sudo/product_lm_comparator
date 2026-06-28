def serialize_supplier(supplier) -> dict:
    categories = [
        {
            "id": sc.category.id,
            "name": sc.category.name,
            "parent_id": sc.category.parent_id,
            "description": sc.category.description,
            "created_at": sc.category.created_at,
        }
        for sc in (supplier.categories or [])
    ]

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
        "categories": categories,
        "contacts": supplier.contacts,
        "order_conditions": supplier.order_conditions,
        "certificates": supplier.certificates,
        "notes": supplier.notes,
    }
