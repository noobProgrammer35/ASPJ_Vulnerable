from flask_sqlalchemy import SQLAlchemy
from flask import current_app,render_template
from hashlib import pbkdf2_hmac
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin,AdminIndexView,expose,BaseView
from flask import Markup
import flask_whooshalchemy
import os


current_app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://dbmsuser:Henry123@localhost/mydb'
current_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
current_app.config['SQLALCHEMY_ECHO'] = True
current_app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'
current_app.config['WHOOSH_BASE'] = 'whoosh'
database = SQLAlchemy(current_app)

class Product(database.Model):
    __tablename__ = 'products'
    __searchable__ = ['Name','Description']
    productid = database.Column(database.Integer,primary_key=True)
    Name = database.Column(database.String(45))
    Description = database.Column(database.String(100))
    stock = database.Column(database.Integer)
    price = database.Column(database.Float(6,2))
    Image = database.Column(database.String)
    Image2 = database.Column(database.String)

    def __init__(self,productName,productDescription,stock,price,imageFileName,Image2):

        self.Name = productName
        self.Description = productDescription
        self.stock = stock
        self.price = price
        self.Image = imageFileName
        self.Image2 = Image2

    def get_id(self):
        return self.productid

    def __repr__(self):
        return "<Product %r>" % self.productid
flask_whooshalchemy.whoosh_index(current_app,Product)

class Customer(database.Model):
    __tablename__ = 'users'
    userid = database.Column(database.Integer,primary_key=True)
    username = database.Column(database.String(50), unique=True)
    fname = database.Column(database.String(45))
    lname = database.Column(database.String(45))
    contact = database.Column(database.Integer())
    email = database.Column(database.String())
    password_hash = database.Column(database.Text())
    password_salt = database.Column(database.Text())
    verified = database.Column(database.Boolean)
    # account = database.relationship('Account',uselist=False,backref='acc_vul',lazy=True)


    def __init__(self,username,fname,lname,contact,password,verified,email):
        self.username = username
        self.fname = fname
        self.lname = lname
        self.contact = contact
        self.email = email
        self.verified = verified
        self.password_salt = self.generate_salt()
        self.password_hash = self.generate_hash(password,self.password_salt)


    def generate_hash(self,plaintext_password,salt):
        password_hash = pbkdf2_hmac(
            'sha256',
            b"%b" % bytes(plaintext_password, 'utf-8'),
            b"%b" % bytes(salt, 'utf-8'),
            10000
        )

    def generate_salt(self):
        salt = os.urandom(16)
        return salt.hex()

class Account(database.Model):
    __tablename__ = 'acc_vul'
    accid = database.Column(database.Integer,primary_key=True,unique=True)
    address = database.Column(database.String(55),nullable=False)
    credit_card = database.Column(database.LargeBinary,nullable=False)
    payment_method = database.Column(database.String(20))
    uid = database.Column(database.Integer,database.ForeignKey('users.userid'))

    def __init__(self,userid):
        self.address = ''
        self.payment_method = 'Credit Card'
        self.uid = userid


class ProductModelView(ModelView):

    create_template = 'product_create.html'
    def my_formatter(view,context,model,name):
        if model.Image:
            Image = "<img src ='../../static/upload/%s' height='100px' width='100px'>" % (model.Image)
            return Markup(Image)
    def name_formatter(view,context,model,name):
        return Markup(model.Name)

    def _formatter(view, context, model, name):
        if model.Image2:
            Image = "<img src ='../../static/upload/%s' height='100px' width='100px'>" % (model.Image2)
            return Markup(Image)

    column_formatters = dict(Image=my_formatter,Name=name_formatter,Image2=_formatter)

admin = Admin(current_app, template_mode='bootstrap3')
admin.add_view(ProductModelView(Product,database.session,endpoint='product'))
admin.add_view(ModelView(Customer,database.session))

