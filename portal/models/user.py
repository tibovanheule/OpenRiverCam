from sqlalchemy import (
    Integer,
    ForeignKey,
    String,
    Column,
    DateTime,
    Enum,
    Float,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship, backref
from models.base import Base
from flask_security import UserMixin, RoleMixin
import uuid

class RolesUsers(Base):
    __tablename__ = "roles_users"
    id = Column(Integer(), primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey("user.id"))
    role_id = Column("role_id", Integer(), ForeignKey("role.id"))


class Role(Base, RoleMixin):
    __tablename__ = "role"
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

def generate_fs_uniquifier():
    # Generate a unique string. Here we use uuid4, you can use any method that suits your needs.
    return str(uuid.uuid4())
    
class User(Base, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(255))
    password = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship(
        "Role", secondary="roles_users", backref=backref("users", lazy="dynamic")
    )
    fs_uniquifier = Column(String(64), unique=True, nullable=False, default=generate_fs_uniquifier)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # Ensure fs_uniquifier is set on instantiation
        if not self.fs_uniquifier:
            self.fs_uniquifier = generate_fs_uniquifier()
