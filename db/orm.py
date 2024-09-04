import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)

    uploads = relationship('Upload', back_populates='user')

class Upload(Base):
    __tablename__ = 'uploads'

    id = Column(Integer, primary_key=True)
    uid = Column(String(36), default=str(uuid.uuid4()), nullable=False)
    filename = Column(String(255), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    finish_time = Column(DateTime)
    status = Column(String(50), nullable=False, default='pending')
    error_message = Column(Text)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='uploads', cascade='all, delete')

    @property
    def upload_path(self):
        # Define how to construct the upload path
        return f"/path/to/uploads/{self.uid}"  # Replace with your actual path logic

    @property
    def is_done(self):
        return self.status == 'done'

# Engine and Session setup
DATABASE_URL = "sqlite:///db/chinook.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)
