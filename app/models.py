from sqlalchemy import String, Integer, Column
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String)

    def __repr__(self):
        return f"<username: {self.username}>"
