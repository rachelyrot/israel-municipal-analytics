from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NationalAverage(Base):
    __tablename__ = "national_averages"
    __table_args__ = (
        UniqueConstraint("indicator_id", "year", name="uq_national_average"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_value: Mapped[float | None] = mapped_column(Float)
    median_value: Mapped[float | None] = mapped_column(Float)
    percentile_25: Mapped[float | None] = mapped_column(Float)
    percentile_75: Mapped[float | None] = mapped_column(Float)
    district_values: Mapped[dict | None] = mapped_column(JSON)  # {"מרכז": 45.2, "צפון": 38.1}
    computed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
