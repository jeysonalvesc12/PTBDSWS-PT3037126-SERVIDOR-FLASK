from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

# Configuração da chave secreta, necessária para proteger contra ataques CSRF (Cross-Site Request Forgery) [cite: 679, 682]
app.config['SECRET_KEY'] = 'Chave forte' 

bootstrap = Bootstrap(app)
moment = Moment(app)

# Mantendo o Context Processor da nossa etapa anterior
@app.context_processor
def injetar_variaveis_globais():
    return dict(meu_nome_fixo="Jason")

# Definição da Classe do Formulário que herda de FlaskForm [cite: 701]
class NameForm(FlaskForm):
    # O validador DataRequired garante que o campo não seja submetido vazio [cite: 730]
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    submit = SubmitField('Enviar')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Rota principal alterada para aceitar métodos GET e POST [cite: 824]
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    
    # Se o formulário for submetido via POST e for válido...
    if form.validate_on_submit():
        old_name = session.get('name')
        
        # Verifica se o nome mudou e envia uma mensagem direcionada ao usuário [cite: 893, 902, 903]
        if old_name is not None and old_name != form.name.data:
            flash('Parece que você alterou o seu nome!')
            
        session['name'] = form.name.data
        
        # Padrão Post/Redirect/Get (PRG) para evitar submissão duplicada [cite: 857, 858]
        return redirect(url_for('index'))
        
    return render_template('index.html', form=form, name=session.get('name'), current_time=datetime.utcnow())

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