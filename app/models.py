from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask.ext.login import UserMixin
from . import db, login_manager
from db_utilities import get_users_connection,execute_query
from psycopg2.extras import DictCursor
from app.api.user_api import confirm_user,change_user_password,email_exists,change_user_email



class Role(db.Model): 
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin):
    #id
    #username
    #email
    
    def __init__(self,id,username,email,confirmed):
        self.id=id
        self.username=username
        self.email=email
        self.confirmed=confirmed
    
    


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        confirm_user(self.id)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        change_user_password(self.id, new_password)
        
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if email_exists(new_email):
            return False
        self.email = new_email
        change_user_email(self.id, new_email)
       
        return True

    def __repr__(self):
        return '<User %r>' % self.username
    
def get_user(attribute,value):
    sql = "SELECT *  FROM  users WHERE %s = '%s'" % (attribute,value)  
    con = get_users_connection()
    results = execute_query(sql, con)
    if not results:
        return None
    user = User(results[0]["id"],results[0]["username"],results[0]["email"],results[0]["confirmed"])
    return user


@login_manager.user_loader
def load_user(user_id):
    return get_user("id",user_id)
