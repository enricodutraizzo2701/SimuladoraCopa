from sqlalchemy import Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
 
from database.base import Base
 
 
class EstatisticaJogadorTorneio(Base):
    __tablename__ = "estatisticas_jogador_torneio"
    __table_args__ = (
        UniqueConstraint("torneio_id", "jogador_id", name="uq_estat_torneio_jogador"),
    )
 
    id: Mapped[int] = mapped_column(primary_key=True)
    torneio_id: Mapped[int] = mapped_column(
        ForeignKey("torneios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    jogador_id: Mapped[int] = mapped_column(
        ForeignKey("jogadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
 
    jogos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gols: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    assistencias: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    defesas: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clean_sheets: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    amarelos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vermelhos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notas_soma: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
 
    # --- relacionamentos ---
    torneio: Mapped["Torneio"] = relationship(back_populates="estatisticas_jogadores")
    jogador: Mapped["Jogador"] = relationship(back_populates="estatisticas_torneio")
 
    @property
    def media_nota(self) -> float:
        """Equivalente à coluna Media_Nota do estatisticas_copa.csv atual."""
        if self.jogos == 0:
            return 0.0
        return round(self.notas_soma / self.jogos, 2)
 
    def __repr__(self) -> str:
        return f"<EstatisticaJogadorTorneio jogador_id={self.jogador_id} gols={self.gols}>"