from typing import Optional
 
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
 
from database.base import Base
 
 
class Confronto(Base):
    __tablename__ = "confrontos"
 
    id: Mapped[int] = mapped_column(primary_key=True)
    torneio_id: Mapped[int] = mapped_column(
        ForeignKey("torneios.id", ondelete="CASCADE"), nullable=False, index=True
    )
 
    fase: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
 
    time_casa_id: Mapped[int] = mapped_column(
        ForeignKey("times.id", ondelete="CASCADE"), nullable=False
    )
    time_fora_id: Mapped[int] = mapped_column(
        ForeignKey("times.id", ondelete="CASCADE"), nullable=False
    )
 
    gols_casa: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gols_fora: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
 
    ordem: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
 
    torneio: Mapped["Torneio"] = relationship(back_populates="confrontos")
    time_casa: Mapped["Time"] = relationship(foreign_keys=[time_casa_id])
    time_fora: Mapped["Time"] = relationship(foreign_keys=[time_fora_id])
 
    @property
    def jogado(self) -> bool:
        return self.gols_casa is not None and self.gols_fora is not None
 
    @property
    def vencedor_id(self) -> Optional[int]:
        if not self.jogado:
            return None
        if self.gols_casa > self.gols_fora:
            return self.time_casa_id
        if self.gols_fora > self.gols_casa:
            return self.time_fora_id
        return None
 
    def __repr__(self) -> str:
        return (
            f"<Confronto id={self.id} fase={self.fase!r} "
            f"{self.time_casa_id}x{self.time_fora_id} "
            f"({self.gols_casa}-{self.gols_fora})>"
        )
 