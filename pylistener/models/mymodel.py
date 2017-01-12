from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    LargeBinary,
    Unicode,
    ForeignKey,
    Table
)
from sqlalchemy.orm import relationship

from .meta import Base

class User(Base):
    """This class defines a User model."""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode, unique=True)
    password = Column(Unicode)
    address_rel = relationship('AddressBook')
    attr_assoc_rel = relationship('UserAttributeLink')


class AddressBook(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    phone = Column(Unicode)
    email = Column(Unicode)
    picture = Column(LargeBinary)
    pic_mime = Column(Unicode)
    user = Column(Integer, ForeignKey('users.id'))


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    label = Column(Unicode)
    desc = Column(Unicode)
    picture = Column(LargeBinary)
    pic_mime = Column(Unicode)
    children = relationship('Attribute')


class Attribute(Base):
    __tablename__ = 'attributes'
    id = Column(Integer, primary_key=True)
    label = Column(Unicode)
    desc = Column(Unicode)
    picture = Column(LargeBinary)
    pic_mime = Column(Unicode)
    cat_id = Column(Integer, ForeignKey('categories.id'))
    user_assoc_rel = relationship('UserAttributeLink')


class UserAttributeLink(Base):
    __tablename__ = "users_attributes_link"
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, primary_key=True)
    attr_id = Column(Integer, ForeignKey('attributes.id'), nullable=False, primary_key=True)
    priority = Column(Integer, default=1, nullable=False)
    num_hits = Column(Integer, default=0, nullable=False)
    user_rel = relationship("User")
    attr_rel = relationship("Attribute")

