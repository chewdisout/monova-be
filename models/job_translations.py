from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class JobTranslation(Base):
    __tablename__ = "job_translations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    lang_code = Column(String(5), nullable=False)

    title = Column(String(255), nullable=True)
    short_description = Column(String(500), nullable=True)
    full_description = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    requirements_text = Column(Text, nullable=True)
    benefits_text = Column(Text, nullable=True)
    housing_details = Column(Text, nullable=True)
    documents_required = Column(Text, nullable=True)
    bonuses = Column(Text, nullable=True)
    language_required = Column(String(80), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("job_id", "lang_code", name="uq_job_lang"),
    )

    job = relationship("Job", back_populates="translations")
