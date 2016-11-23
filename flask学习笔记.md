## Flask 学习笔记

### 一、为路由新增正则表达式的支持
参考：[https://segmentfault.com/q/1010000000125259](https://segmentfault.com/q/1010000000125259)

``` python
#!/usr/bin/env python
# -*- coding=utf-8 -*-

from flask import Flask
from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
    def __init__(self, map, *args):
        self.map = map
        self.regex = args[0]

app = Flask(__name__)
app.url_map.converters['regex'] = RegexConverter

@app.route('/')
def index():
    return '<h1> Hello Flask! </h1>'

@app.route('/user/<name>')
def user(name):
    return '<h1> hello {0} </h1>'.format(name.encode('utf-8'))

@app.route('/test/<regex("[0-9]{3}"):user_id>/')
def test(user_id):
    return 'your id is {0}'.format(user_id)


if __name__ == '__main__':
    app.run(debug=True)

```


### 二、利用`livereload`监控flask项目目录，当文件有改动时自动刷新浏览器（常用与开发测试，提高效率）
#### 1、安装
> pip install livereload
> pip install flask-script

#### 2、使用
``` python
# hello.py

from flask import Flask
from flask.ext.script import Manager
from livereload import Server

app = Flask(__name__)
app.config['DEBUG'] = True
manager = Manager(app)

@manager.command
def dev():
	live_server = Server(app.wsgi_app)
    live_server.watch('**/*.*')	# 可用正则表达式
    liver_server.serve(open_url=True)

if __name__ == '__main__':
	manager.run()
```
运行 `python hello.py dev`


### 三、模板
模板中文文档：[http://docs.jinkan.org/docs/jinja2/templates.html#id2](http://docs.jinkan.org/docs/jinja2/templates.html#id2)

								视图函数
						render_template('index.html')
									|（通过上下文与模板共享变量）
								   模板
							视图函数引擎(jinja2)
									|(渲染)
								   HTML

#### 1、模板中常用的过滤器
| 过滤器名 | 说明 |
|--------|--------|
|	safe	|	渲染值时不转义    |
|	capitalize	|	把值的首字母转换成大写，其他字母转换成小写	|
|	lower	|	把值转换成小写	|
|	upper	|	把值转换成大写	|
|	title	|	把值中每个单词的首字母都转换成大写	|
|	trim	|	把值的首尾空格去掉	|
|	striptags	| 渲染之前把值中所有的HTML标签都删掉	|
|	tojson	|	这个函数把给定的对象转换为 JSON 表示，如果你要动态生成 JavaScript 这里有一个非常有用的例子。|
查看更多内置的过滤器：`app.jinja_env.filters`

#### 2、自定义模板过滤器
``` python
# 方法一
@app.template_filter('md')
def markdown_to_html(txt):
	from markdown import markdown
	return markdown(txt)

# 方法二
def markdown_to_html(txt):
	from markdown import markdown
	return markdown(txt)
app.jinja_env.filters['md'] = markdown_to_html

# 在模板中引用(跟标准过滤器一样使用)
{{ content|md }}
```

#### 3、上下文处理器
``` python
@app.context_processor
def utility_processor():
    def format_price(amount, currency=u'€'):
        return u'{0:.2f}{1}.format(amount, currency)
    return dict(format_price=format_price)

# 在模板中使用
{{ format_price(0.33) }}
```


### 四、表单
安装flask表单插件
> pip install flask-wtf


#### 1、表单中常用的验证函数：
| 验证函数 | 说明 |
|--------|--------|
|    Email    |    验证电子邮件地址    |
|	EqualTo	|	比较两个字段的值；常用于要求输入两次密码进行确认的情况|
|	IPAddress	|	验证ipv4地址	|
|	Length	|	验证输入字符串的长度	|
|	NumberRange	|	验证输入值在数字范围	|
|	Optional	|	无输入值时跳过其他验证函数	|
|	Regexp	|	使用正则表达式验证输入值	|
|	URL	|	验证url	|
|	AnyOf	|	确保输入值再可选值列表中	|
|	NoneOf	|	确保输入值不在可选值列表中	|


#### 2、表单中自定义验证函数
比如我想以下表单中name字段值中第一个字母不能是数字（当然可以用正则表达式来实现，此处只为演示如何自定义验证函数）

``` python
from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import Required, ValidationError

# 方法一
def check_field_not_digit(form, field):
	if field.data[0].isdigit():
		raise ValidationError('word first letter not number!')

class NameForm(Form):
	name = StringField("What's your name?", validators=[Required(), check_field_not_digit])

# 方法二: 表单类中定义了以validate_开头且后面跟字段名的方法
class NameForm(Form):
	name = StringField("What's your name?", validators=[Required()])

	def validate_name(self, field):
		if field.data[0].isdigit():
			raise ValidationError('word first letter not number!')
```

参考：[http://wtforms.simplecodes.com/docs/0.6.2/validators.html#custom-validators](http://wtforms.simplecodes.com/docs/0.6.2/validators.html#custom-validators)
亦可查看源码(源码在你的flask-wtf安装路径下)，观摩内置的验证函数是怎么实现的
> ~/.virtualenvs/flask/lib/python2.7/site-packages/wtforms/validators.py


