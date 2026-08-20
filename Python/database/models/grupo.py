from typing import List
 
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
 
from database.base import Base
 
 
class Grupo(Base):
    __tablename__ = "grupos"
    __table_args__ = (
        UniqueConstraint("torneio_id", "nome", name="uq_grupos_torneio_nome"),
    )
 
    id: Mapped[int] = mapped_column(primary_key=True)
    torneio_id: Mapped[int] = mapped_column(
        ForeignKey("torneios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(20), nullable=False)
 
    torneio: Mapped["Torneio"] = relationship(back_populates="grupos")
    times: Mapped[List["GrupoTime"]] = relationship(
        back_populates="grupo", cascade="all, delete-orphan",
        order_by="desc(GrupoTime.pts), desc(GrupoTime.sg), desc(GrupoTime.gp)",
    )
 
    def __repr__(self) -> str:
        return f"<Grupo id={self.id} nome={self.nome!r}>"
 
 
class GrupoTime(Base):
    __tablename__ = "grupo_times"
    __table_args__ = (
        UniqueConstraint("grupo_id", "time_id", name="uq_grupo_times_grupo_time"),
    )
 
    id: Mapped[int] = mapped_column(primary_key=True)
    grupo_id: Mapped[int] = mapped_column(
        ForeignKey("grupos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    time_id: Mapped[int] = mapped_column(
        ForeignKey("times.id", ondelete="CASCADE"), nullable=False, index=True
    )
 
    pts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    j: Mapped[int] = mapped_column(Integer, default=0, nullable=False)   # jogos
    v: Mapped[int] = mapped_column(Integer, default=0, nullable=False)   # vitórias
    e: Mapped[int] = mapped_column(Integer, default=0, nullable=False)   # empates
    d: Mapped[int] = mapped_column(Integer, default=0, nullable=False)   # derrotas
    gp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # gols pró
    gc: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # gols contra
    sg: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # saldo de gols
 
    grupo: Mapped["Grupo"] = relationship(back_populates="times")
    time: Mapped["Time"] = relationship()
 
    def __repr__(self) -> str:
        return f"<GrupoTime time_id={self.time_id} pts={self.pts} sg={self.sg}>"
 