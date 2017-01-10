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

# user_address_link = Table('user_address', Base.metadata,
#     user_id=Column(Integer, ForeignKey('users.id'), nullable=False),
#     address_id=Column(Integer, ForeignKey('addresses.id'), nullable=False)
# )

user_attributes_link = Table(
    'user_attributes',
    Base.metadata,
    Column("user_id", Integer, ForeignKey('users.id'), nullable=False),
    Column("attributes_id", Integer, ForeignKey('attributes.id'), nullable=False),
    Column("priority", Integer, default=1, nullable=False),
    Column("num_hits", Integer, default=0, nullable=False)
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Unicode, unique=True)
    password = Column(Unicode)
    address_rel = relationship(
        'AddressBook'
    )
    attr_rel = relationship(
        'Attributes',
        secondary=user_attributes_link,
        back_populates="user_rel"
    )


class AddressBook(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    phone = Column(Unicode)
    email = Column(Unicode)
    picture = Column(LargeBinary)
    user = Column(Integer, ForeignKey('users.id'))



class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    label = Column(Unicode)
    desc = Column(Unicode)
    picture = Column(LargeBinary)
    children = relationship('Attributes')


class Attributes(Base):
    __tablename__ = 'attributes'
    id = Column(Integer, primary_key=True)
    label = Column(Unicode)
    desc = Column(Unicode)
    picture = Column(LargeBinary)
    cat_id = Column(Integer, ForeignKey('categories.id'))
    user_rel = relationship(
        'User',
        secondary=user_attributes_link,
        back_populates='attr_rel'
    )
