#CSDL
from sqlalchemy import Column, DateTime, Float, Enum, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from bookstore import db, app
from datetime import datetime
from enum import Enum as UserEnum
from flask_login import UserMixin


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    ADMIN = 1
    INVENT_MANAGE = 2
    STAFF = 3
    USER = 4




class Genre(BaseModel):
    __tablename__ = 'genre'

    name = Column(String(20), nullable=False)
    sachs = relationship('Book', backref='genre', lazy=True)

    def __str__(self):
        return self.name


class Book(BaseModel):
    __tablename__ = 'book'

    name = Column(String(40), nullable=False)
    author = Column(String(100))
    price = Column(Float, default=0)
    image = Column(String(200))
    active = Column(Boolean, default=True)
    theloai_id = Column(Integer, ForeignKey(Genre.id), nullable=False)
    receipt_details = relationship('ReceiptDetails', backref='book', lazy=True)


    def __str__(self):
        return self.name

class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    email = Column(String(50))
    active = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    receipts = relationship('Receipt', backref='user', lazy=True)
    def __str__(self):
        return self.name

class Receipt(BaseModel):
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    details = relationship('ReceiptDetails', backref='receipt', lazy=True)

class ReceiptDetails(db.Model):
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False, primary_key=True)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False, primary_key=True)
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0)


with app.app_context():
    if __name__ == '__main__':
        db.create_all()

        # t1= Genre(name='T??m l??')
        # t2= Genre(name='Trinh th??m')
        # t3= Genre(name='Ti???u thuy???t')
        # t4= Genre(name='K?? n??ng')
        # t5= Genre(name='Khoa h???c')

        # db.session.add(t1)
        # db.session.add(t2)
        # db.session.add(t3)
        # db.session.add(t4)
        # db.session.add(t5)

        # for s in booklist:
        #     sach = Book(name=s['name'], author=s['description'], price=s['price'], image=s['image'], theloai_id=s['category_id'])
        #
        #     db.session.add(sach)
        #
        # db.session.commit()