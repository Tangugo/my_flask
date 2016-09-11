#!/usr/bin/env python
# -*- coding=utf-8 -*-


from flask_wtf import Form
#  from wtforms import StringField, SubmitField
#  from wtforms.validators import Required
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import Required, ValidationError, Regexp


class NameForm(Form):
    name = StringField("What's your name?", validators=[Required()])

    sbumit = SubmitField('Submit')