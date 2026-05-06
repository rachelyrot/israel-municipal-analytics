from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)   # e.g. "POP_TOTAL"
    name_he: Mapped[str] = mapped_column(String(100), nullable=False)            # שם בעברית
    domain: Mapped[str] = mapped_column(String(30), nullable=False)              # population / education / ...
    unit: Mapped[str | None] = mapped_column(String(20))                         # נפש / % / ₪
    is_percentage: Mapped[bool] = mapped_column(Boolean, default=False)
    higher_is_better: Mapped[bool | None] = mapped_column(Boolean)               # לצורך דירוג
    cbs_column_variants: Mapped[list | None] = mapped_column(JSON, default=list) # כותרות עמודה ב-Excel
    description_he: Mapped[str | None] = mapped_column(String(300))
