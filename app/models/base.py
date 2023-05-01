from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.db.base_class import Base


class Video(Base):
    __tablename__ = "videos"
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str]
    channel_id: Mapped[str]

    subtitles: Mapped[list["Subtitle"]] = relationship(back_populates="video")


class Subtitle(Base):
    __tablename__ = "subtitles"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    video_id = mapped_column(ForeignKey("videos.id"))
    start_time: Mapped[float]
    end_time: Mapped[float]
    text: Mapped[str]

    video = relationship("Video", back_populates="subtitles")
