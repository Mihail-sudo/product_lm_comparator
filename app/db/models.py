from sqlalchemy import (
    Column, Integer, String, Text, DECIMAL, Boolean, 
    TIMESTAMP, Date, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    city = Column(String(100), nullable=False)
    region = Column(String(100))
    address = Column(Text)
    website = Column(String(255))
    foundation_year = Column(Integer, CheckConstraint('foundation_year > 1900'))
    rating = Column(DECIMAL(3, 2), CheckConstraint('rating >= 0 AND rating <= 5'), default=0)
    rating_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    status = Column(String(20), CheckConstraint("status IN ('active', 'inactive', 'blocked')"), default='active')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    categories = relationship('SupplierCategory', back_populates='supplier', cascade='all, delete-orphan')
    contacts = relationship('Contact', back_populates='supplier', cascade='all, delete-orphan')
    order_conditions = relationship('OrderCondition', back_populates='supplier', cascade='all, delete-orphan')
    certificates = relationship('Certificate', back_populates='supplier', cascade='all, delete-orphan')
    notes = relationship('UserNote', back_populates='supplier', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_suppliers_city', 'city'),
        Index('idx_suppliers_region', 'region'),
        Index('idx_suppliers_rating', 'rating'),
        Index('idx_suppliers_status', 'status'),
        # Для полнотекстового поиска (только PostgreSQL)
        Index('idx_suppliers_name_trgm', 'name', postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'}),
    )
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}', city='{self.city}')>"


class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    suppliers = relationship('SupplierCategory', back_populates='category', cascade='all, delete-orphan')
    parent = relationship('Category', remote_side=[id], backref='children')
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class SupplierCategory(Base):
    __tablename__ = 'supplier_categories'
    
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
    is_main = Column(Boolean, default=False)
    
    # Relationships
    supplier = relationship('Supplier', back_populates='categories')
    category = relationship('Category', back_populates='suppliers')

    # Indexes
    __table_args__ = (
        Index('idx_supplier_categories_supplier', 'supplier_id'),
        Index('idx_supplier_categories_category', 'category_id'),
    )
    
    def __repr__(self):
        return f"<SupplierCategory(supplier_id={self.supplier_id}, category_id={self.category_id})>"


class Contact(Base):
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    contact_type = Column(String(30), CheckConstraint("contact_type IN ('phone', 'email', 'telegram', 'whatsapp', 'viber', 'other')"), nullable=False)
    contact_value = Column(String(255), nullable=False)
    contact_person = Column(String(100))
    is_primary = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    supplier = relationship('Supplier', back_populates='contacts')

    # Indexes
    __table_args__ = (
        Index('idx_contacts_supplier', 'supplier_id'),
    )
    
    def __repr__(self):
        return f"<Contact(id={self.id}, type='{self.contact_type}', value='{self.contact_value}')>"


class OrderCondition(Base):
    __tablename__ = 'order_conditions'
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    min_order_quantity = Column(DECIMAL(10, 2))
    min_order_unit = Column(String(30), CheckConstraint("min_order_unit IN ('kg', 'ton', 'piece', 'box', 'pallet', 'liter', 'other')"))
    price_per_unit = Column(DECIMAL(10, 2))
    price_currency = Column(String(3), default='RUB')
    price_negotiable = Column(Boolean, default=True)
    delivery_terms = Column(Text)
    delivery_region = Column(String(100))
    delivery_cost = Column(DECIMAL(10, 2))
    payment_terms = Column(Text)
    lead_time_days = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    supplier = relationship('Supplier', back_populates='order_conditions')
    category = relationship('Category')

    # Indexes
    __table_args__ = (
        Index('idx_order_conditions_supplier', 'supplier_id'),
    )
    
    def __repr__(self):
        return f"<OrderCondition(id={self.id}, supplier_id={self.supplier_id})>"


class Certificate(Base):
    __tablename__ = 'certificates'
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    certificate_name = Column(String(255), nullable=False)
    certificate_type = Column(String(50), CheckConstraint("certificate_type IN ('quality', 'safety', 'organic', 'halal', 'kosher', 'iso', 'other')"))
    issuing_authority = Column(String(255))
    issued_date = Column(Date)
    expiry_date = Column(Date)
    file_url = Column(String(255))
    is_valid = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    supplier = relationship('Supplier', back_populates='certificates')

    # Indexes
    __table_args__ = (
        Index('idx_certificates_supplier', 'supplier_id'),
        Index('idx_certificates_valid', 'supplier_id', 'is_valid'),
    )
    
    def __repr__(self):
        return f"<Certificate(id={self.id}, name='{self.certificate_name}', is_valid={self.is_valid})>"


class UserNote(Base):
    __tablename__ = 'user_notes'
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    note_text = Column(Text, nullable=False)
    note_type = Column(String(30), CheckConstraint("note_type IN ('general', 'quality', 'price', 'delivery', 'communication', 'other')"))
    rating_impact = Column(Integer, CheckConstraint('rating_impact BETWEEN -2 AND 2'))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    supplier = relationship('Supplier', back_populates='notes')

    # Индексы
    __table_args__ = (
        Index('idx_user_notes_supplier', 'supplier_id'),
    )
    
    def __repr__(self):
        return f"<UserNote(id={self.id}, supplier_id={self.supplier_id}, type='{self.note_type}')>"
