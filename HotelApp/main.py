from flask import render_template, redirect, request, session, jsonify, url_for
from HotelApp import app, utils, login, decorator
from HotelApp.admin import *
from HotelApp.models import *
from flask_login import login_user, login_required
import hashlib, os, json
from datetime import datetime
import cloudinary.uploader
from HotelApp.models import UserRole
import math



# Trang Client
@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar_path = None

        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']

                utils.add_user(name=name, username=username,
                               password=password, email=email,
                               avatar=avatar_path)
                return redirect(url_for('index'))
            else:
                err_msg = "Mật khẩu không khớp!!!"
        except Exception as ex:
            err_msg = "Lỗi : " + str(ex)

    return render_template('register.html', err_msg=err_msg)


@app.route('/api/comments', methods=['post'])
@login_required
def add_comment():
    data = request.json
    content = data.get('content')
    room_id = data.get('room_id')

    try:
        c = utils.add_comment(content=content, room_id=room_id)
    except:
        return {'status': 404, 'err_msg': 'Comment không thành công!'}

    return {'status': 201, 'comment': {
            'id': c.id,
            'content': c.content,
            'created_date': c.created_date,
            'user': {
                'username': current_user.username,
                'avatar': current_user.avatar
            }}}


@app.route('/login', methods=['get', 'post'])
def user_signin():
    err_msg = ""
    if request.method.__eq__('POST'):
        try:
            username = request.form.get('username')
            password = request.form.get('password')

            user = utils.check_login(username=username,
                                     password=password)
            if user:
                login_user(user=user)
                return redirect(url_for('index'))
            else:
                err_msg = "Sai Username or password"
        except Exception as ex:
            err_msg = "Lỗi đăng nhập: " + str(ex)
    return render_template('login.html', err_msg=err_msg)


@app.route('/logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))


@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/')
def index():
    category = utils.read_category()
    cate_id = request.args.get('category_id')
    kw = request.args.get('kw')
    empty = request.args.get('active')
    rooms = utils.read_rooms(cate_id=cate_id, kw=kw, empty=empty)

    return render_template('index.html', rooms = rooms,
                           category=category)


# Trang chi tiết phòng
@app.route("/index/<int:room_id>")
def room_detail(room_id):
    room = utils.get_room_by_id(room_id)
    comments = utils.get_comments(room_id=room_id,
                                  page=int(request.args.get('page', 1)))

    return render_template('room-detail.html', room=room, comments=comments,
                           pages=math.ceil(utils.count_comment(room_id=room_id)/app.config['COMMENT_SIZE']))
# Đăng nhập


@app.route('/admin/login', methods=['post', 'get'])
def login_admin():
    err_msg = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password', '')
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        user = User.query.filter(User.username == username.strip(), User.password == password.strip()).first()
        if user:
            login_user(user=user)

            return redirect('/admin')
        else:
            err_msg = "Đăng nhập không thành công"

    return redirect('/admin')


# Trang tạm dùng để lấy thông tin đặt phòng của khách điền từ form
@app.route('/payment', methods=['post'])
def add_to_cart():
    if request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        price = float(request.form.get('price'))
        local = int(request.form.get('local'))
        foreign = int(request.form.get('foreign'))
        in_date = request.form.get('in_date')
        out_date = request.form.get('out_date')
        guest = request.form.get('guest')
        phone = request.form.get('phone')
        reg = utils.getReg()
        date = datetime.strptime(out_date, '%Y-%m-%d') - datetime.strptime(in_date, '%Y-%m-%d')
        quantity = local + foreign
        total = float(price) * date.days

# Kiểm tra quy định
        if int(date.days) <= 0:
            total = 0
            date = datetime.strptime(in_date, '%Y-%m-%d') - datetime.strptime(in_date, '%Y-%m-%d')

        if local + foreign <= reg.max:
            if quantity > 2:
                total = total + (quantity - 2) * total * reg.sercharse
        else:
            quantity = 0
            total = 0

        if foreign > 0:
            total *= reg.increase
            is_foreign = True
        else:
            is_foreign = False
# Lưu thông tin đặt hàng vào cart
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    cart[id] = {
        "id": id,
        "name": name,
        "price": price,
        "date": date.days,
        "quantity": quantity,
        "is_foreign": is_foreign,
        "total": total,
        "sum": 1,
        "guest": guest,
        "phone": phone
    }
    session['cart'] = cart
# Tính và lưu tổng tiền trong cart
    sum , sum_total = utils.cart_stats(cart)
    cart_info = {
        "sum": sum,
        "sum_total": sum_total
    }
    return render_template("payment.html", cart_info=cart_info)
# Trang thanh toán


@app.route('/payment', methods=['get', 'post'])
def payment():
    sum, sum_total = utils.cart_stats(session.get('cart'))
    cart_info = {
        "sum": sum,
        "sum_total": sum_total
    }
    return render_template('payment.html', cart_info=cart_info)


# Xử lí thanh toán và lưu hóa đơn
@app.route('/api/pay', methods=['post'])
def pay():
    if utils.add_receipt(session.get('cart')):
        del session['cart']
        return (jsonify({
            "message": "Đã thêm hóa đơn thành công!",
            "err_code": 200,
        }))

    return jsonify({
        "message": "Thanh toán thất bại!!!"
    })

# Trang thuê phòng tại sảnh
@app.route('/admin/checkin')
def checkin():
    rooms = utils.read_rooms()
    return render_template('admin/checkin.html', rooms=rooms)

# Trang thuê phòng đặt trước.....(Chưa thực thi)
@app.route('/admin/e-checkin')
def e_checkin():
    return render_template('admin/e-checkin.html')

# Trang trả phòng
@app.route('/admin/checkout')
def checkout():
    return render_template('admin/checkout.html')


# Xử lí thay đổi trạng thái phòng
@app.route('/api/changeActive', methods=['GET','POST'])
def changeActive():
    data = json.loads(request.data)
    room_id = str(data.get('id'))
    utils.changeActive(room_id)
    return jsonify({})


# Xử lí xóa phòng trong cart ở trang thanh toán
@app.route('/api/delCart', methods = ['post'])
def delCart():
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']

    data = json.loads(request.data)
    id = str(data.get('id'))

    if id in cart:
        cart.pop(id)
    session['cart'] = cart

    if not cart:
        del session['cart']

    return jsonify({})


@login.user_loader
def user_load(user_id):
    return User.query.get(user_id)


if __name__ == '__main__':
    app.run(debug=True, port='5555')