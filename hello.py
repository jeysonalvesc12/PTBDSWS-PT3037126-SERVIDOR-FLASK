from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

app = Flask(__name__)

bootstrap = Bootstrap(app)
moment = Moment(app)


@app.context_processor
def injetar_variaveis_globais():
    return dict(nome="Jeyson")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@app.route('/identificacao')
def identificacao():
   
    return render_template('identificacao.html')

@app.route('/contexto')
def contexto():
    # Aqui também não precisamos mais passar o nome!
    user_agent = request.headers.get('User-Agent')
    ip = request.remote_addr
    host = request.host
    return render_template('contexto.html', user_agent=user_agent, ip=ip, host=host)

if __name__ == '__main__':
    app.run(debug=True)
