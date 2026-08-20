from typing import TYPE_CHECKING, List, Optional
 
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint 
from sqlalchemy.orm import Mapped, mapped_column, relationship  
 
from database.base import Base

if TYPE_CHECKING:
    from Python.database.models.jogador import Jogador
    from Python.database.models.universo import Universo
 
 
class Time(Base):
    __tablename__ = "times"
    __table_args__ = (
        UniqueConstraint("universo_id", "nome", name="uq_times_universo_nome"),
    )
 
    id: Mapped[int] = mapped_column(primary_key=True)
    universo_id: Mapped[int] = mapped_column(
        ForeignKey("universos.id", ondelete="CASCADE"), nullable=False, index=True
    )
 
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    tecnico: Mapped[Optional[str]] = mapped_column(String(120))
    escudo: Mapped[Optional[str]] = mapped_column(String(255))  
 
    ataque: Mapped[int] = mapped_column(Integer, nullable=False)
    meio: Mapped[int] = mapped_column(Integer, nullable=False)
    defesa: Mapped[int] = mapped_column(Integer, nullable=False)
    goleiro: Mapped[int] = mapped_column(Integer, nullable=False)
 
    universo: Mapped["Universo"] = relationship(back_populates="times")
    jogadores: Mapped[List["Jogador"]] = relationship(
        back_populates="time", cascade="all, delete-orphan"
    )
 
    def __repr__(self) -> str:
        return f"<Time id={self.id} nome={self.nome!r}>"
 