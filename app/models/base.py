from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Video(Base):
    __tablename__ = "videos"
    id = Column(String, primary_key=True)
    title = Column(String)
    channel_id = Column(String)
    video_url = Column(String)

    subtitles = relationship("Subtitle", back_populates="video")


class Subtitle(Base):
    __tablename__ = "subtitles"
    id = Column(Integer, primary_key=True)
    video_id = Column(String, ForeignKey("videos.id"))
    start_time = Column(Float)
    end_time = Column(Float)
    text = Column(String)

    video = relationship("Video", back_populates="subtitles")
