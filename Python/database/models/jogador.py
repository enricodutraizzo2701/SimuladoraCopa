from typing import TYPE_CHECKING, Optional
 
from sqlalchemy import String, Integer, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
 
from database.base import Base

if TYPE_CHECKING:
    from database.models import EstatisticaJogadorTorneio
    from Python.database.models.time import Time
 
POSICOES_VALIDAS = (
    "GOL", "ZAG", "LAT", "LD", "LE",
    "VOL", "MC", "MEI", "MD", "ME",
    "PE", "PD", "ATA", "SA",
)
 
STATUS_VALIDOS = ("Titular", "Reserva")
 
 
class Jogador(Base):
    __tablename__ = "jogadores"
    __table_args__ = (
        CheckConstraint(
            "posicao IN (" + ",".join(f"'{p}'" for p in POSICOES_VALIDAS) + ")",
            name="ck_jogadores_posicao_valida",
        ),
        CheckConstraint(
            "status IN ('Titular','Reserva')",
            name="ck_jogadores_status_valido",
        ),
        CheckConstraint("ovr >= 0 AND ovr <= 99", name="ck_jogadores_ovr_range"),
    )
 
    id: Mapped[int] = mapped_column(primary_key=True)
    time_id: Mapped[int] = mapped_column(
        ForeignKey("times.id", ondelete="CASCADE"), nullable=False, index=True
    )
 
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    posicao: Mapped[str] = mapped_column(String(5), nullable=False)
    ovr: Mapped[int] = mapped_column(Integer, nullable=False)
    capitao: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(10), default="Titular", nullable=False)
 
    # --- relacionamentos ---
    time: Mapped["Time"] = relationship(back_populates="jogadores")
    estatisticas_torneio: Mapped[list["EstatisticaJogadorTorneio"]] = relationship(
        back_populates="jogador", cascade="all, delete-orphan"
    )
 
    def __repr__(self) -> str:
        return f"<Jogador id={self.id} nome={self.nome!r} posicao={self.posicao}>"
 