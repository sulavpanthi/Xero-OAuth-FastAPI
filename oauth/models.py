import uuid
from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from core.db import Base, get_db_context


class UserOAuthToken(Base):
    __tablename__ = "user_oauth_tokens"
    id = Column(UUID, default=uuid.uuid4, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    @classmethod
    def create(cls):
        with get_db_context() as session:
            new_user = cls()
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
        return new_user.id

    @classmethod
    def save_tokens(cls, user_id, tokens):
        expires_in = tokens["expires_in"]
        print("tokens-----", tokens)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        with get_db_context() as session:
            user = session.query(cls).filter(cls.id == user_id).first()
            user.access_token = tokens["access_token"]
            user.refresh_token = tokens["refresh_token"]
            user.expires_at = expires_at
            session.commit()
