"""
Provider model
"""

from sqlalchemy import Column, String, Text
from .base import Base, TimestampMixin


class Provider(Base, TimestampMixin):
    """Provider entity"""
    __tablename__ = "providers"
    
    provider_id = Column(String(16), primary_key=True)
    provider_name = Column(String(255), nullable=False)
    primary_domain = Column(String(255), nullable=False, unique=True)
    provider_type = Column(String(50), nullable=False)  # Vendor, Community, Directory, Official
    contact_url = Column(Text, nullable=True)
