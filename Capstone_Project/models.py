from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)  # MSSQL needs a length for unique/index
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)