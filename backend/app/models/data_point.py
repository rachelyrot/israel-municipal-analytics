from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DataPoint(Base):
    __tablename__ = "data_points"
    __table_args__ = (
        UniqueConstraint("municipality_id", "indicator_id", "year", name="uq_data_point"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    municipality_id: Mapped[int] = mapped_column(ForeignKey("municipalities.id"), nullable=False)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[float | None] = mapped_column(Float)
    source_file: Mapped[str | None] = mapped_column(String(100))  # שם קובץ המקור
    sheet_name: Mapped[str | None] = mapped_column(String(100))   # שם הגיליון
    notes: Mapped[str | None] = mapped_column(String(300))
    ingested_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
