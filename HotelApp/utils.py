import hashlib
from HotelApp.models import User, Room, Category, Receipt, ReceiptDetail, UserRole, Comment
from flask_login import current_user
from HotelApp.admin import *
from sqlalchemy import func
from flask import request


# Truy vấn loại phòng
def read_category():
    return Category.query.all()
    # categories = Category.query
    # return categories.all()


# Truy vấn phòng
def read_rooms(cate_id=None, empty=None, kw=None):

    rooms = Room.query.join(Category).add_columns(Category.price, Category.image, Category.name)
    if cate_id:
        rooms = rooms.filter(Room.category_id == cate_id)

    if empty:
        rooms = rooms.filter(Room.active == empty)

    if kw:
        rooms = rooms.filter(Room.name.contains(kw))

    return rooms.group_by(Room.id).all()


# Lấy thông tin phòng thông qua id
def get_room_by_id(room_id):
    room = Room.query.join(Category, Room.category_id == Category.id)\
        .add_columns(Category.price, Category.image, Category.description).filter(Room.id == room_id)

    return room.all()[0]


# Thêm tài khoản
def add_user(name, username, password, email, avatar):
    password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
    user = User(name=name,
                username=username,
                password=password,
                email=email,
                avatar=avatar)
    try:
        db.session.add(user)
        db.session.commit()
        return True
    except:
        return False

#
# def cart_update(cart):
#     total_amount, total_quantity = 0, 0
#     if cart:
#         for r in cart.values():
#             total_quantity = r['quantity']
#             total_amount = r['price']
#     return total_quantity, total_amount

# Hàm tính tổng tiền trong cart


def cart_stats(cart):
    sum, sum_total = 0, 0
    if cart:
        for r in cart.values():
            sum = sum + r["sum"]
            sum_total = sum_total + r["total"]

    return sum, sum_total


# Thêm hóa đơn - Chi tiết hóa đơn
def add_receipt(cart):
    if cart:
        sum_total = 0
        guest = ''
        phone = ''
        for r in list(cart.values()):
            sum_total += r['total']
            guest = r['guest']
            phone = r['phone']

        receipt = Receipt(customer_id=1, total=sum_total, guest=guest, phone=phone)
        db.session.add(receipt)

        for r in list(cart.values()):
            detail = ReceiptDetail(receipt=receipt,
                                   room_id=int(r["id"]),
                                   date=r["date"],
                                   quantity=r["quantity"],
                                   is_foreign=r["is_foreign"],
                                   price=r["price"])
            db.session.add(detail)

        try:
            db.session.commit()
            return True
        except Exception as ex:
            print(ex)

    return False


# Thay đổi trạng thái phòng thông qua id
def changeActive(room_id):
    room = Room.query.get(room_id)
    room.active = not room.active
    db.session.add(room)
    db.session.commit()


# Lấy thông tin của qui định
def getReg():
    reg = Regulations.query
    return reg.first()


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


def cate_sta():
    return db.session.query(Category.id, Category.name, func.count(Room.id)).\
                            join(Room, Category.id.__eq__(Room.category_id), isouter=True).\
                            group_by(Category.id)


def total_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Room.id, Room.name, func.sum(ReceiptDetail.price * ReceiptDetail.date))\
        .join(ReceiptDetail, ReceiptDetail.room_id.__eq__(Room.id), isouter=True)\
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id))\
        .group_by(Room.id, Room.name)

    if kw:
        p = p.filter(Room.name.contains(kw))
    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))
    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))

    return p.all()


def add_comment(content, room_id):
    c = Comment(content=content, room_id=room_id, user=current_user)

    db.session.add(c)
    db.session.commit()

    return c


def get_comments(room_id, page=1):
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size

    return Comment.query.filter(Comment.room_id.__eq__(room_id))\
                        .order_by(-Comment.id).slice(start, start + page_size).all()


def count_comment(room_id):
    return Comment.query.filter(Comment.room_id.__eq__(room_id)).count()
