#!/usr/bin/env python
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask import Flask, render_template, request, redirect, url_for, session, json

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager


app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(80), unique=True)
    applications_user = db.relationship('Application_receipt', backref='applic_user', lazy='dynamic')

    def __init__(self, login, password, email, username):
        self.login = login
        self.password = password
        self.email = email
        self.username = username


    def __repr__(self):
        return '<User %r>' % self.username

class Complect(db.Model):
    __tablename__ = 'complect'
    id = db.Column(db.INTEGER, primary_key=True)
    applications_receipt = db.relationship('Application_receipt', backref='applic', lazy='dynamic')
    sort_id = db.Column(db.INTEGER, db.ForeignKey('sort.id'))
    manufacturer_id = db.Column(db.INTEGER,db.ForeignKey('manufacturer.id'))


    def __init__(self,sort_id, manufacturer_id):
        self.sort_id = sort_id
        self.manufacturer_id = manufacturer_id

class Type(db.Model):
    __tablename__ = 'type'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(45), unique=True)
    price = db.Column(db.INTEGER)
    sorts = db.relationship('Sort', backref='sort', lazy='dynamic')

    def __init__(self,name,price):
        self.name = name
        self.price = price

class Sort(db.Model):
    __tablename__= 'sort'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(45))
    types_id = db.Column(db.INTEGER, db.ForeignKey('type.id'))
    complects = db.relationship('Complect', backref='complect1', lazy='dynamic')

    def __init__(self,name,types_id):
        self.name = name
        self.types_id = types_id

class Manufacturer(db.Model):
    __tablename__ = 'manufacturer'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(45))
    complects = db.relationship('Complect', backref='complect2', lazy='dynamic')

    def __init__(self,name):
        self.name = name


class Application_receipt(db.Model):
    __tablename__ = 'application_receipt'
    id = db.Column(db.INTEGER, primary_key=True)
    complect_id = db.Column(db.INTEGER, db.ForeignKey('complect.id'))
    quantity = db.Column(db.INTEGER)
    date_adoption = db.Column(db.Date)
    date_issue = db.Column(db.Date)
    provider_id = db.Column(db.INTEGER,db.ForeignKey('user.id'))
    price = db.Column(db.INTEGER)
    confirmed = db.Column(db.BOOLEAN)

    def __init__(self,complect_id, quantity,date_adoption,date_issue, provider_id,price,confirmed):
        self.complect_id = complect_id
        self.quantity = quantity
        self.date_adoption = date_adoption
        self.date_issue = date_issue
        self.provider_id = provider_id
        self.price = price
        self.confirmed = confirmed

class Sklad(db.Model):
    __tablename__ = 'sklad'
    id = db.Column(db.INTEGER, primary_key = True)
    application_id = db.Column(db.INTEGER, db.ForeignKey('application_receipt.id'))
    issued = db.Column(db.BOOLEAN, default=False)

    def __init__(self,application_id,issued):
        self.application_id = application_id
        self.issued = issued

if __name__ == '__main__':
    manager.run()






