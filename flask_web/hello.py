#!/usr/bin/env python
# -*- coding=utf-8 -*-


import os

from flask import (Flask, request, current_app, g, session, make_response,
                   redirect, render_template, url_for, flash)
from werkzeug.routing import BaseConverter
from flask.ext.script import Manager, Shell
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.mail import Mail, Message
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import Required, ValidationError, Regexp
from livereload import Server


class RegexConverter(BaseConverter):
    def __init__(self, map, *args):
        self.map = map
        self.regex = args[0]


class Listconverter(BaseConverter):
    def to_python(self, value):
        return value.split(',')
    def to_url(self, values):
        return ','.join(BaseConverter.to_url(value)
                        for value in values)

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USER_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FALSKY_MAIL_SENDER'] = 'luckytanggu@163.com'
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flask]'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

app.url_map.converters['regex'] = RegexConverter
app.url_map.converters['list'] = Listconverter
bootstrap = Bootstrap(app)
manager = Manager(app)
db = SQLAlchemy(app)
migrate  = Migrate(app, db)
manager.add_command('db', MigrateCommand)
mail = Mail(app)



@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FALSKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))

@app.route('/user/<name>')
def user(name):
    #  return '<h1> hello {0} </h1>'.format(name.encode('utf-8'))
    #name = '- Hi tab'
    return render_template('user.html', name=name)

@app.route('/test_regex/<regex("[0-9]{3}"):user_id>/')
def test_regex(user_id):
    return 'your id is {0}'.format(user_id)

@app.template_filter('md')
def markdown_to_html(txt):
    from markdown import markdown
    return markdown(txt)

def read_md(filename):
    with open(filename, 'r') as md_file:
        content = reduce(lambda x, y: x+y, md_file.readlines())
    return content.decode('utf-8')

@app.context_processor
def inject_methods():
    return dict(read_md=read_md('./test_md'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_err(e):
    return render_template("500.html"), 500

@manager.command
def dev():
    live_server = Server(app.wsgi_app)
    live_server.watch("**/*.*")
    live_server.serve(open_url=True)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command('shell', Shell(make_context=make_shell_context))

def check_char_len(form, field):
    if field.data[0].isdigit():
        raise ValidationError('must char!')
    else:
        if len(field.data) < 8:
            raise ValidationError('char length must larget 8')

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template, + '.html', **kwargs)
    mail.send(msg)

class NameForm(Form):
    name = StringField("What's your name?", validators=[Required()])

    sbumit = SubmitField('Submit')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    age = db.Column(db.Integer)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


if __name__ == '__main__':
    #  app.run(debug=True)
    manager.run()
