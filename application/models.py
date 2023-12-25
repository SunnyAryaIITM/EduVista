from application.database import db
from utils.enums import Status
import re

user_role = db.Table('user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

user_address = db.Table('user_address',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('address_id', db.Integer, db.ForeignKey('addresses.id'), primary_key=True)
)

approval_user = db.Table('approval_user',
    db.Column('approval_id', db.Integer, db.ForeignKey('approvals.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.String, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    addresses = db.relationship('Address', secondary=user_address, lazy='subquery',
        backref=db.backref('users', lazy=True))
    roles = db.relationship('Role', secondary=user_role, lazy='subquery',
        backref=db.backref('users', lazy=True))

    def __init__(self, name, email, phone, password):
        self.name = name
        self.set_email(email)
        self.set_phone(phone)
        self.set_password(password)

    def __repr__(self):
        return f'<User {self.id}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'image': self.image,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'image': self.image,
            'address': [address.serialize() for address in self.addresses],
            'roles': [role.serialize() for role in self.roles]
        }
    
    def set_email(self, email):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email address")

        self.email = email

    def set_phone(self, phone):
        phone_pattern = r'^[6-9]\d{9}$'
        if not re.match(phone_pattern, phone):
            raise ValueError("Invalid phone number")

        self.phone = phone

    def set_password(self, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(password) > 16:
            raise ValueError("Password must be at most 16 characters long")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one number")
        if not any(char in '!@#$%^&*()_-+={}[]|\:;"<>,.?/~`' for char in password):
            raise ValueError("Password must contain at least one special character")

        self.password = password
    
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Role {self.id}>'
    
    def serialize(self):
        return {
            'id': self.id,
            'role': self.name
        }
    
class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    line1 = db.Column(db.String(100), nullable=False)
    line2 = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    pin_code = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    
    def __init__(self, line1, line2, district, state, pin_code, country):
        self.line1 = line1
        self.line2 = line2
        self.district = district
        self.state = state
        self.pin_code = pin_code
        self.country = country

    def __repr__(self):
        return f'<Address {self.id} {self.line1}>'
    
    def serialize(self):
        return {
            'id' : self.id,
            'line1' : self.line1,
            'line2' : self.line2,
            'district' : self.district,
            'state' : self.state,
            'pin_code' : self.pin_code,
            'country' : self.country
        }

class Approval(db.Model):
    __tablename__ = 'approvals'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Integer, nullable=False, default=Status.PENDING['code'])
    approval_type = db.Column(db.Integer, nullable=False)
    status_by_admin = db.Column(db.Integer, nullable=True, default=Status.PENDING['code'])
    status_by_SuAdmin = db.Column(db.Integer, nullable=True, default=Status.PENDING['code'])
    users = db.relationship('User', secondary=approval_user, lazy='subquery',
        backref=db.backref('approvals', lazy=True))
    
    def __init__(self, status, status_by_admin, status_by_SuAdmin):
        self.status = status
        self.status_by_admin = status_by_admin
        self.status_by_SuAdmin = status_by_SuAdmin

    def __repr__(self):
        return f'<Approval {self.id}>'
    
    def serialize(self):
        return {
            'id' : self.id,
            'status' : self.status,
            'approval_type' : self.approval_type,
            'status_by_admin' : self.status_by_admin,
            'status_by_SuAdmin' : self.status_by_SuAdmin,
            'users' : [user.serialize() for user in self.users]
        }
    
    def getApprovedUsers(self):
        if self.status == Status.APPROVED['code']:
            return [user.serialize() for user in self.users]
        else:
            return {'message' : 'No users approved yet'}
        
    def getPendingUsers(self):
        if self.status == Status.PENDING['code']:
            return [user.serialize() for user in self.users]
        else:
            return {'message' : 'No users pending for approval'}
        
    