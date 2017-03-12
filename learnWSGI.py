#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wsgiref.simple_server import make_server
from cgi import escape
from urlparse import parse_qs


html = """
<html>
<body>
   <form method="post" action="">
        <p>
           Age: <input type="text" name="age" value="%(age)s">
        </p>
        <p>
            Hobbies:
            <input
                name="hobbies" type="checkbox" value="software"
                %(checked-software)s
            > Software
            <input
                name="hobbies" type="checkbox" value="tunning"
                %(checked-tunning)s
            > Auto Tunning
        </p>
        <p>
            <input type="submit" value="Submit">
        </p>
    </form>
    <p>
        Age: %(age)s<br>
        Hobbies: %(hobbies)s
    </p>
</body>
</html>
"""


def application(environ, start_response):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    d = parse_qs(environ['QUERY_STRING'])
    age = d.get('age', [''])[0] # 返回age对应的值
    hobbies = d.get('hobbies', []) # 以list形式返回所有的hobbies
    # 防止脚本注入
    age = escape(age)
    hobbies = [escape(hobby) for hobby in hobbies]

    response_body = html % {
        'checked-software': ('', 'checked')['software' in hobbies],
        'checked-tunning': ('', 'checked')['tunning' in hobbies],
        'age': age or 'Empty',
        'hobbies': ', '.join(hobbies or ['No Hobbies?'])
    }
 #小技巧：   "Age: %(age)s" % {'age':12}   输出：  'Age: 12'
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(response_body)))
    ]
    start_response(status, response_headers)

    return response_body

def application1(environ, start_response):

    response_body = 'hello world!'

    status = '200 OK'

    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body]

# 中间件
class Upperware:
   def __init__(self, app):
      self.wrapped_app = app

   def __call__(self, environ, start_response):
      for data in self.wrapped_app(environ, start_response):
        yield data.upper()

wrapped_app = Upperware(application)

httpd = make_server (
    '127.0.0.1',
    8051, # port
    application1 # WSGI application，此处就是一个函数
)


httpd.serve_forever()

print 'end'

