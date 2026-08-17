from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-muito-forte-aqui-123456'

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    submit = SubmitField('Enviar')



@app.context_processor
def injetar_variaveis_globais():
    return dict(nome="Jeyson")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Parece que você mudou seu nome!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, current_time=datetime.utcnow(), name=session.get('name'))

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
