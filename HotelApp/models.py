from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from HotelApp import db
from flask_login import UserMixin
from flask_login import current_user
from datetime import datetime
from enum import Enum as UserEnum


class HotelModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    def __str__(self):
        return self.name


class UserRole(UserEnum):
    USER = 1
    ADMIN = 2


class User(HotelModel, UserMixin):
    __tablename__ = 'user'

    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    email = Column(String(100))
    active = Column(Boolean, default=True)
    avatar = Column(String(100))
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    receipts = relationship('Receipt', backref='user', lazy=True)
    comments = relationship('Comment', backref='user', lazy=True)

    def __str__(self):
        return self.name

    def is_accessible(self):
        return current_user.is_authenticated


class Category(HotelModel):
    __tablename__ = 'category'

    rooms = relationship('Room', backref='category', lazy=True)
    price = Column(Float, default=0)
    image = Column(String(100))
    description = Column(String(255))


class Room(HotelModel):
    __tablename__ = 'room'

    active = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    receipt_details = relationship('ReceiptDetail', backref='room', lazy=True)
    comments = relationship('Comment', backref='room', lazy=True)


class Comment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(255), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return self.content


class Receipt(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.today())
    customer_id = Column(Integer, ForeignKey(User.id))
    guest = Column(String(50))
    phone = Column(String(20))
    total = Column(Float, default=0)
    details = relationship('ReceiptDetail',
                           backref='receipt', lazy=True)


class ReceiptDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False)
    price = Column(Integer, default=0)
    date = Column(Integer, default=0)
    quantity = Column(Integer, default=0)
    is_foreign = Column(Boolean, default=False)


class Regulations(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    sercharse = Column(Float, default=0.25)
    increase = Column(Float, default=1.5)
    max = Column(Integer, default=3)


if __name__ == '__main__':
    db.create_all()