from urllib import response

from HotelApp import admin, db, utils, app
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, Admin, AdminIndexView
from HotelApp.models import Category, Room, User, Receipt, ReceiptDetail, Regulations, UserRole
from flask_login import current_user, logout_user
from flask import redirect, request


class Logout(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


class Login(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/login.html')

    def is_accessible(self):
        return not current_user.is_authenticated


# Chỉ dành cho user là ADMIN
class AuthenticatedModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class Register(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/register.html')


class BaseView(BaseView):

    def is_accessible(self):
        return current_user.is_authenticated


class CheckIn(BaseView):
    @expose('/')
    def index(self):
        rooms = utils.read_rooms()
        return self.render('admin/checkin.html', rooms=rooms)


class CheckOut(BaseView):
    @expose('/')
    def index(self):
        rooms = utils.read_rooms()
        return self.render('admin/checkout.html', rooms=rooms)


class StatsView(BaseView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        return self.render('admin/stats.html', stats=utils.total_stats(kw=kw, from_date=from_date, to_date=to_date))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class RoomView(AuthenticatedModelView):
    can_view_details = True
    column_searchable_list = ['name']
    column_labels = {
        'name': 'Tên phòng',
        'category': 'Loại phòng'
    }


class CategoryView(AuthenticatedModelView):
    can_view_details = True
    column_searchable_list = ['name', 'price']
    column_exclude_list = ['image']
    column_labels = {
        'name': 'Tên phòng',
        'price': 'Giá',
        'description': 'Mô tả'
    }


class ReCView(AuthenticatedModelView):
    can_view_details = True
    column_searchable_list = ['phone', 'guest']
    column_exclude_list = ['user']
    column_labels = {
        'created_date': 'Ngày tạo',
        'guest': 'Tên khách hàng',
        'phone': 'SĐT',
        'total': 'Tổng tiền'
    }


class ReCDetailView(AuthenticatedModelView):
    can_view_details = True
    column_searchable_list = ['price']
    column_labels = {
        'price': 'Giá',
        'date': 'Số ngày',
        'quantity': 'Số lượng',
        'is_foreign': 'Có khách nước ngoài',
        'room': 'Tên phòng',
        'receipt': 'Hóa đơn'
    }


class UserView(AuthenticatedModelView):
    can_view_details = True


class RegulationView(AuthenticatedModelView):
    can_view_details = True
    column_labels = {
        'sercharse': 'Phụ thu phí',
        'increase': 'Nhân hệ số',
        'max': 'Tối đa',
    }


class AdminIndex(AdminIndexView):
    @expose('/')
    def __index__(self):
        return self.render('admin/index.html',
                            sta=utils.cate_sta())


admin = Admin(app=app, name='My Hotel', template_mode='bootstrap4', index_view=AdminIndex())
admin.add_view(UserView(User, db.session))
admin.add_view(CategoryView(Category, db.session))
admin.add_view(RoomView(Room, db.session))
admin.add_view(ReCView(Receipt, db.session))
admin.add_view(ReCDetailView(ReceiptDetail, db.session))
admin.add_view(RegulationView(Regulations, db.session))
admin.add_view(CheckIn(name=None))
admin.add_view(CheckOut(name=None))
admin.add_view(Login(name=None))
admin.add_view(StatsView(name='Stats'))
admin.add_view(Logout(name=None))


