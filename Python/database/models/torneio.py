from datetime import datetime, timezone
from typing import List, Optional
 
from sqlalchemy import String, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
 
from database.base import Base
 
FASES_VALIDAS = ("grupos", "fim_grupos", "mata_mata", "encerrado")
 
 
class Torneio(Base):
    __tablename__ = "torneios"
    __table_args__ = (
        CheckConstraint(
            "fase_atual IN (" + ",".join(f"'{f}'" for f in FASES_VALIDAS) + ")",
            name="ck_torneios_fase_valida",
        ),
    )
 
    id: Mapped[int] = mapped_column(primary_key=True)
    universo_id: Mapped[int] = mapped_column(
        ForeignKey("universos.id", ondelete="CASCADE"), nullable=False, index=True
    )
 
    fase_atual: Mapped[str] = mapped_column(String(20), default="grupos", nullable=False)
 
    is_final_round: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
 
    campeao_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("times.id", ondelete="SET NULL"), nullable=True
    )
 
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    encerrado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
 
    universo: Mapped["Universo"] = relationship(back_populates="torneios")
    campeao: Mapped[Optional["Time"]] = relationship(foreign_keys=[campeao_id])
 
    grupos: Mapped[List["Grupo"]] = relationship(
        back_populates="torneio", cascade="all, delete-orphan"
    )
    confrontos: Mapped[List["Confronto"]] = relationship(
        back_populates="torneio", cascade="all, delete-orphan"
    )
    estatisticas_jogadores: Mapped[List["EstatisticaJogadorTorneio"]] = relationship(
        back_populates="torneio", cascade="all, delete-orphan"
    )
 
    def __repr__(self) -> str:
        return f"<Torneio id={self.id} fase={self.fase_atual!r}>"
 