#!/usr/bin/env python
# -*- coding=utf-8 -*-


from threading import Thread

from flask_mail import Message

from . import mail, create_app

app = create_app('default')

def send_async_email(msg):
    with app.app_context():
        mail.send()

def send_email(to, subject, template, **kargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'], + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kargs)
    msg.html = render_template(template + '.html', **kargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
