# CONTROLLER
from flask import render_template, request, redirect, url_for, session, jsonify
from bookstore import app, login
import utils
import math
from flask_login import login_user, logout_user, login_required
import cloudinary.uploader
from models import UserRole


@app.route("/")
def home():
    nav_index = 0
    books = utils.load_books()
    gens = utils.load_genres()

    genre_id = request.args.get('genre_id')
    kw = request.args.get('keyword')
    from_price = request.args.get('from_price')
    to_price = request.args.get('to_price')
    if genre_id:
        nav_index = int(genre_id)
    page = request.args.get('page', 1)

    counter = utils.count_books()
    books = utils.load_books(genre_id=genre_id,
                             kw=kw,
                             from_price=from_price,
                             to_price=to_price,
                             page=int(page))

    return render_template('index.html',
                           genres=gens,
                           books=books,
                           index=nav_index,
                           page=math.ceil(counter / app.config['PAGE_SIZE']), )


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    # trường name trong input sẽ nhảy vào đây
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        confirm = request.form.get('confirm')
        avatar_path = None

        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']

                utils.add_user(name=name,
                               username=username,
                               password=password,
                               email=email,
                               avatar=avatar_path)
                return redirect(url_for('user_signin'))
            else:
                err_msg = 'Mật khẩu KHÔNG khớp'
        except Exception as ex:
            err_msg = "Hệ thống có lỗi: " + str(ex)

    return render_template('register.html', err_msg=err_msg)


@app.route('/user-login', methods=['GET', 'POST'])
def user_signin():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)

            next = request.args.get('next', 'home')
            return redirect(url_for(next))
        else:
            err_msg = 'Thông tin đăng nhập KHÔNG chính xác!!!'

    return render_template('login.html', err_msg=err_msg)


@app.route('/admin-login', methods=['post'])
def signin_admin():
    username = request.form.get('username')
    password = request.form.get('password')

    user = utils.check_login(username=username,
                             password=password,
                             role=UserRole.ADMIN)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))


@app.route('/books/<int:book_id>')
def book_detail(book_id):
    book = utils.get_book_by_id(book_id)
    return render_template('details.html', b=book)


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/api/pay', methods=['POST'])
@login_required
def pay():
    try:
        utils.add_receipt(session.get('cart'))
        del session['cart']
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})


@app.context_processor
def common_reponse():
    return {
        'cart_stats' : utils.count_cart(session.get('cart'))
    }

@app.route('/cart')
def cart():
    return render_template('cart.html',
                           stats=utils.count_cart(session.get('cart')))


@app.route('/api/add-cart', methods=['POST'])
def add_to_cart():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')

    cart = session.get('cart')
    if not cart:
        cart = {}

    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': 1
        }

    session['cart'] = cart

    return jsonify(utils.count_cart(cart))

@app.route('/api/update-cart', methods=['put'])
def update_cart():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    cart = session.get('cart')
    if cart and id in cart:
        cart[id]['quantity'] = quantity
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/delete-cart/<book_id>', methods=['delete'])
def delete_cart(book_id):
    cart = session.get('cart')

    if cart and book_id in cart:
        del cart[book_id]
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))



if __name__ == '__main__':
    from bookstore.admin import *

    app.run(debug=True)