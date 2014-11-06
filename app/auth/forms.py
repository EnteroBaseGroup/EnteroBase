from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User
from ..api import user_api


class LoginForm(Form):
    email_or_username = StringField('Email or Username', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                           Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    
    firstname = StringField('Firstname', validators=[
          Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z]*$', 0,
                                            'names must have only letters, '
                                            '')])        
    lastname = StringField('Lastname', validators=[
             Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z]*$', 0,
                                               'names must have only letters, '
                                               '')])            
    department = StringField('Department', validators=[
                Required(), Length(1, 64)])  
    institution = StringField('Institution', validators=[
             Required(), Length(1, 64)]) 
    
    city = StringField('City', validators=[
             Required(), Length(1, 64)]) 
    country = StringField('Country', validators=[
                 Required(), Length(1, 64)])         
          
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if user_api.email_exists(field.data):
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if user_api.username_exists(field.data):
            raise ValidationError('Username already in use.')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[Required()])
    password = PasswordField('New password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if not user_api.email_exists(field.data):
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(Form):
    email = StringField('New Email', validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if user_api.email_exists(field.data):
            raise ValidationError('Email already registered.')
