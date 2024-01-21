import uuid

from sqlalchemy import Column, ForeignKey, String, Numeric, Uuid, Integer
from sqlalchemy.orm import relationship

from .database import Base


class Menu(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # id = Column(Uuid,
    #             primary_key=True,
    #             index=True, default=uuid.uuid4)
    title = Column(String, unique=True, index=True)
    description = Column(String, default='')
    children = relationship(
        "SubMenu",
        back_populates="parent",
        cascade="all, delete",
        passive_deletes=True,
    )


class SubMenu(Base):
    __tablename__ = "submenus"

    id = Column(Integer, primary_key=True, autoincrement= True)
    # id = Column(Uuid,
    #             primary_key=True,
    #             index=True, default=uuid.uuid4)
    title = Column(String, unique=True, index=True)
    description = Column(String, default='')
    menu_id = Column(Integer, ForeignKey("menus.id", ondelete="CASCADE"))
    # menu_id = Column(Uuid, ForeignKey("menus.id", ondelete="CASCADE"))
    parent = relationship("Menu", back_populates="children")
    children = relationship(
        "Dish",
        back_populates="parent",
        cascade="all, delete",
        passive_deletes=True,
    )


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # id = Column(Uuid,
    #             primary_key=True,
    #             index=True, default=uuid.uuid4)
    title = Column(String, unique=True, index=True)
    description = Column(String, default='')
    price = Column(Numeric(10, 2), default=0.00)
    submenu_id = Column(Integer, ForeignKey("submenus.id", ondelete="CASCADE"))
    # submenu_id = Column(Uuid, ForeignKey("submenus.id", ondelete="CASCADE"))
    parent = relationship("SubMenu", back_populates="children")
