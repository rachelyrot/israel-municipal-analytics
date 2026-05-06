from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Municipality(Base):
    __tablename__ = "municipalities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    symbol_cbs: Mapped[str | None] = mapped_column(String(10), unique=True)  # סמל הרשות
    municipality_type: Mapped[str | None] = mapped_column(String(30))        # עיר / מועצה מקומית / מועצה אזורית
    district: Mapped[str | None] = mapped_column(String(30))                 # מחוז
    region: Mapped[str | None] = mapped_column(String(30))                   # נפה
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    socioeconomic_cluster: Mapped[int | None] = mapped_column(Integer)       # אשכול 1-10
    name_aliases: Mapped[list | None] = mapped_column(JSON, default=list)    # שמות חלופיים לזיהוי
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
