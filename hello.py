# A very simple Flask Hello World app for you to get started with...
from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello_world():
    return '<p>Alterações por meio do PythonAnyWhere -> GitHub</p><table><tr><td><b>Aluno:</b></td><td>Jeyson</td></tr><tr><td><b>Prontuário:</b></td><td>PT3037126</td></tr></table>'

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, {}!</h1>'.format(name)
