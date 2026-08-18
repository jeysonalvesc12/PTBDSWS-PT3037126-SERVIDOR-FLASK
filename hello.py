from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Chave forte' 

bootstrap = Bootstrap(app)
moment = Moment(app)

@app.context_processor
def injetar_variaveis_globais():
    return dict(meu_nome_fixo="Jason")

class NameForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    submit = SubmitField('Enviar')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Rota principal (Home) agora está limpa, apenas mostrando a hora e o nome da sessão
@app.route('/')
def index():
    # Pegamos o 'name' da sessão caso o usuário já tenha preenchido o formulário
    return render_template('index.html', name=session.get('name'), current_time=datetime.utcnow())

# NOVA ROTA: Exclusiva para o formulário
@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    form = NameForm()
    
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Parece que você alterou o seu nome!')
            
        session['name'] = form.name.data
        
        # Redireciona para a própria página de formulário após envio (Padrão PRG)
        return redirect(url_for('formulario'))
        
    return render_template('formulario.html', form=form, name=session.get('name'))

@app.route('/identificacao')
def identificacao():
    return render_template('identificacao.html')

@app.route('/contexto')
def contexto():
    user_agent = request.headers.get('User-Agent')
    ip = request.remote_addr
    host = request.host
    return render_template('contexto.html', user_agent=user_agent, ip=ip, host=host)

if __name__ == '__main__':
    app.run(debug=True)