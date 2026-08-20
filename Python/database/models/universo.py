from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
 
from sqlalchemy import String, DateTime, UniqueConstraint  # type: ignore[reportMissingImports]
from sqlalchemy.orm import Mapped, mapped_column, relationship  # type: ignore[reportMissingImports]
 
from database.base import Base

if TYPE_CHECKING:
    from database.models import HallDaFamaEdicao, Torneio
    from Python.database.models.time import Time
 
 
class Universo(Base):
    __tablename__ = "universos"
    __table_args__ = (
        UniqueConstraint("nome", name="uq_universos_nome"),
    )
 
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
 
    # --- relacionamentos ---
    times: Mapped[List["Time"]] = relationship(
        back_populates="universo", cascade="all, delete-orphan"
    )
    torneios: Mapped[List["Torneio"]] = relationship(
        back_populates="universo", cascade="all, delete-orphan"
    )
    edicoes_hall_da_fama: Mapped[List["HallDaFamaEdicao"]] = relationship(
        back_populates="universo", cascade="all, delete-orphan"
    )
 
    def __repr__(self) -> str:
        return f"<Universo id={self.id} nome={self.nome!r}>"
 