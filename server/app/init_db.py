from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserInfo(Base):
    __tablename__ = "access_form_data"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False)

def initialize_tables(engine):
    Base.metadata.create_all(bind=engine)
    return