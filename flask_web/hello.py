#!/usr/bin/env python
# -*- coding=utf-8 -*-


from flask import (Flask, request, current_app, g, session, make_response,
                   redirect, render_template)
from werkzeug.routing import BaseConverter
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
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


app = Flask(__name__)
app.config['DEBUG'] = True
app.url_map.converters['regex'] = RegexConverter
app.url_map.converters['list'] = Listconverter
bootstrap = Bootstrap(app)
manager = Manager(app)


@app.route('/')
def index():
    #  user_agent = request.headers.get('User-Agent')
    #  print dir(current_app)
    #  print '\n'
    #  print dir(g)
    #  print '\n'
    #  print dir(session)
    #  return '<p>{0}</p>'.format(dir(request))
    #  return '<h1> Hello Flask! </h1>'
    #  return redirect('https://www.baidu.com')
    #  response = make_response(('<h1>This document carries a cookie!</h1>'))
    #  response.set_cookie('answer', '42')
    #  return response
    return render_template('index.html')

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


if __name__ == '__main__':
    #  app.run(debug=True)
    manager.run()
