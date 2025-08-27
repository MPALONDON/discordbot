from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class MemberLog(Base):
    __tablename__ = "member_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False)
    member_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # "join" or "leave"
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)

class Poll(Base):
    __tablename__ = "polls"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(String(200), nullable=False)
    options: Mapped[str] = mapped_column(Text, nullable=False)

class MusicQueue(Base):
    __tablename__ = "music_queue"
    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    guild_id : Mapped[int] = mapped_column(Integer, nullable=False)
    title : Mapped[str] = mapped_column(String(200), nullable=False)
    url : Mapped[str] = mapped_column(Text, nullable=False)
