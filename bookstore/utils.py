# tương tác csdl - MODEL
from models import Genre, Book, User, UserRole, Receipt, ReceiptDetails
from bookstore import app, db
from flask_login import current_user
import hashlib

from sqlalchemy import func
from sqlalchemy.sql import extract
import utils


def load_genres():
    return Genre.query.all()


def load_books(genre_id=None, kw=None, from_price=None, to_price=None, page=1):
    books = Book.query.filter(Book.active.__eq__(True))

    if genre_id:
        books = books.filter(Book.theloai_id == genre_id)
    if kw:
        books = books.filter(Book.name.contains(kw))
    if from_price:
        books = books.filter(Book.price.__ge__(from_price))
    if to_price:
        books = books.filter(Book.price.__le__(to_price))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return books.slice(start, end).all()


def count_books():
    return Book.query.filter(Book.active.__eq__(True)).count()


def get_book_by_id(book_id):
    return Book.query.get(book_id)


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(),
                username=username.strip(),
                password=password,
                email=kwargs.get('email'),
                avatar=kwargs.get('avatar'))

    db.session.add(user)
    db.session.commit()


def check_login(username, password, role=UserRole.USER):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password),
                                 User.user_role.__eq__(role)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_receipt(cart):
    if cart:
        receipt = Receipt(user=current_user)
        db.session.add(receipt)

        for c in cart.values():
            d = ReceiptDetails(receipt=receipt, book_id=c['id'], quantity=c['quantity'], unit_price=c['price'])
            db.session.add(d)

        db.session.commit()

        return receipt


def count_cart(cart):
    total_quantity, total_amount = 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }


def genre_stats():
    return db.session.query(Genre.id, Genre.name, func.count(Genre.id))\
                            .join(Book, Genre.id.__eq__(Book.theloai_id), isouter=True)\
                            .group_by(Genre.id, Genre.name).all()

def book_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Genre.id, Genre.name, func.sum(ReceiptDetails.quantity * ReceiptDetails.unit_price))\
                         .join(ReceiptDetails, ReceiptDetails.book_id.__eq__(Genre.id), isouter=True)\
                         .join(Receipt, Receipt.id.__eq__(ReceiptDetails.receipt_id))\
                         .group_by(Genre.id, Genre.name)

    if kw:
        p = p.filter(Genre.name.contains(kw))
    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))
    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))

    return p.all()


def book_month_stats(month):
    return db.session.query(extract('month', Receipt.created_date),
                            func.sum(ReceiptDetails.quantity * ReceiptDetails.unit_price))\
                            .join(ReceiptDetails, ReceiptDetails.receipt_id.__eq__(Receipt.id))\
                            .filter(extract('month', Receipt.created_date) == month)\
                            .group_by(extract('month', Receipt.created_date)).all()