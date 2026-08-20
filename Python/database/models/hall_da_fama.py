from typing import Optional
 
from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
 
from database.base import Base
 
 
class HallDaFamaEdicao(Base):
    __tablename__ = "hall_da_fama_edicoes"
    __table_args__ = (
        UniqueConstraint("universo_id", "edicao_numero", name="uq_hdf_universo_edicao"),
    )
 
    id: Mapped[int] = mapped_column(primary_key=True)
    universo_id: Mapped[int] = mapped_column(
        ForeignKey("universos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edicao_numero: Mapped[int] = mapped_column(Integer, nullable=False)  # "Edicao_1" -> 1
 
    campeao: Mapped[str] = mapped_column(String(120), nullable=False)
    vice: Mapped[str] = mapped_column(String(120), nullable=False)
    terceiro: Mapped[str] = mapped_column(String(120), nullable=False)
    quarto: Mapped[str] = mapped_column(String(120), nullable=False)
 
    artilheiro_nome: Mapped[Optional[str]] = mapped_column(String(120))
    artilheiro_gols: Mapped[Optional[int]] = mapped_column(Integer)
 
    assistente_nome: Mapped[Optional[str]] = mapped_column(String(120))
    assistente_qtd: Mapped[Optional[int]] = mapped_column(Integer)
 
    melhor_goleiro_nome: Mapped[Optional[str]] = mapped_column(String(120))
    melhor_goleiro_cs: Mapped[Optional[int]] = mapped_column(Integer)  # clean sheets
 
    melhor_jogador_nome: Mapped[Optional[str]] = mapped_column(String(120))
    melhor_jogador_media: Mapped[Optional[float]] = mapped_column(Float)
 
    universo: Mapped["Universo"] = relationship(back_populates="edicoes_hall_da_fama")
 
    def __repr__(self) -> str:
        return f"<HallDaFamaEdicao edicao={self.edicao_numero} campeao={self.campeao!r}>"
 