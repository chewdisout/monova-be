from database import Base
from sqlalchemy import Column, Integer, Text, String, Float, Boolean, DateTime
from datetime import datetime, timezone

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Display / identity
    title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    reference_code = Column(String(64), nullable=True, unique=True)

    # Location
    country = Column(String(2), nullable=False, index=True)
    city = Column(String(120), nullable=True)
    workplace_address = Column(String(255), nullable=True)

    # Category / type
    category = Column(String(80), nullable=False, index=True)
    employment_type = Column(String(40), nullable=True)
    shift_type = Column(String(80), nullable=True)

    # Pay & benefits
    salary_from = Column(Float, nullable=True)
    salary_to = Column(Float, nullable=True)
    currency = Column(String(8), nullable=True, default="EUR")
    salary_type = Column(String(16), nullable=True)
    is_net = Column(Boolean, default=False)
    housing_provided = Column(Boolean, default=False)
    housing_details = Column(Text, nullable=True)
    transport_provided = Column(Boolean, default=False)
    bonuses = Column(Text, nullable=True)

    # Requirements
    min_experience_years = Column(Integer, nullable=True)
    language_required = Column(String(80), nullable=True)
    documents_required = Column(Text, nullable=True)
    driving_license_required = Column(Boolean, default=False)

    # Content
    short_description = Column(String(500), nullable=False)
    full_description = Column(Text, nullable=False)
    responsibilities = Column(Text, nullable=True)
    requirements_text = Column(Text, nullable=True)
    benefits_text = Column(Text, nullable=True)

    # Control
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
