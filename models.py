import uuid 
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="admin")  
    distributions = relationship("Distribution", back_populates="user")

class Member(Base):
    __tablename__ = "members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    identity_no = Column(String, unique=True, index=True, nullable=False)
    # False = belum diambil, True = sudah diambil
    status = Column(Boolean, default=False)
    distributions = relationship("Distribution", back_populates="member")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    stock = Column(Integer, default=0)
    unit = Column(String, nullable=False)

class Distribution(Base):
    __tablename__ = "distributions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="distributions")
    member = relationship("Member", back_populates="distributions")