from flask_wtf import FlaskForm
#vulnerability: does not escape string causses XSS ,-- comp with known vulnerability
from wtforms import StringField,PasswordField,IntegerField,validators,TextAreaField,SelectField


class RegisterForm(FlaskForm):
    username = StringField('Username')
    fname = StringField('Name')
    lname = StringField('Name')
    contact = StringField('Contact')
    email = StringField('Email')
    password = PasswordField('Password')
    confirm = PasswordField('Confirm Password')


class LoginForm(FlaskForm):
    username = StringField('Username',validators=[validators.DataRequired('Username is required!')])
    password = PasswordField('Password',validators=[validators.DataRequired('Password is required')])


class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired('Username is required!')])
    password = PasswordField('Password', validators=[validators.DataRequired('Password is required')])
    # token = StringField('Token', validators=[validators.DataRequired(), validators.Length(6, 6)])


# class TwoFactorForm(FlaskForm):
#     token = StringField('Token', validators=[validators.DataRequired(), validators.Length(6, 6)])
#
#
# class AccountForm(FlaskForm):
#     address = TextAreaField('Address',validators=[validators.Length(max=55,message='Please do not exceed more than 55 characters')])
#     payment_method = SelectField('Payment Method',choices = [('Credit Card','Credit Card')])
#     credit_card = StringField('Credit Card',validators=[validators.Length(min=16,message='Credit card should be 16 digit'),validators.regexp('^(?:4[0-9]{12}(?:[0-9]{3})?|[25][1-7][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})$',message='wrongdog')])
#
#
# class EmailForm(FlaskForm):
#     email = StringField('Email',validators=[validators.DataRequired('Email is required'),validators.Email(message='Please enter valid email address')])
#
# class PasswordResetForm(FlaskForm):
#     password = PasswordField('Password',validators=[validators.DataRequired('Password is required'),validators.EqualTo('confirm',message='Password does not match'),validators.Length(min=8,message='Password minimum 8 characters'),validators.Regexp('^.*(?=.{8,10})(?=.*[a-zA-Z])(?=.*?[A-Z])(?=.*\d)[a-zA-Z0-9!@£$%^&*()_+={}?:~\[\]]+$',message='Password must contain at least 8 characters with uppercase,lowercase,symbol and numbers.')])
#     confirm = PasswordField('Confirm Password')
