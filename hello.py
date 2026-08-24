from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Chave forte' 

bootstrap = Bootstrap(app)
moment = Moment(app)

# Formulário da Home (image_6a4d65.png e image_6a4d9c.png)
class HomeForm(FlaskForm):
    nome = StringField('Informe o seu nome', validators=[DataRequired()])
    sobrenome = StringField('Informe o seu sobrenome:', validators=[DataRequired()])
    instituicao = StringField('Informe a sua Instituição de ensino:', validators=[DataRequired()])
    
    # SelectField cria o menu suspenso (dropdown) com as opções de disciplinas
    disciplina = SelectField('Informe a sua disciplina:', 
                             choices=[('DSWA5', 'DSWA5'), 
                                      ('DWBA4', 'DWBA4'), 
                                      ('Gestão de projetos', 'Gestão de projetos')])
    submit = SubmitField('Submit')

# Formulário de Login (image_6a540c.png)
class LoginForm(FlaskForm):
    # render_kw adiciona o atributo placeholder no HTML, deixando o texto dentro do campo
    usuario = StringField('', render_kw={"placeholder": "Usuário ou e-mail"}, validators=[DataRequired()])
    senha = PasswordField('', render_kw={"placeholder": "Informe a sua senha"}, validators=[DataRequired()])
    submit = SubmitField('Enviar')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Rota Principal (Home)
@app.route('/', methods=['GET', 'POST'])
def index():
    form = HomeForm()
    
    if form.validate_on_submit():
        session['nome'] = form.nome.data
        session['sobrenome'] = form.sobrenome.data
        session['instituicao'] = form.instituicao.data
        session['disciplina'] = form.disciplina.data
        return redirect(url_for('index'))
        
    ip = request.remote_addr
    host = request.host
    return render_template('index.html', form=form, ip=ip, host=host, current_time=datetime.utcnow())

# Rota de Login modificada
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    # Se o formulário for enviado e validado com sucesso...
    if form.validate_on_submit():
        # Salva o usuário (e-mail) digitado na sessão[cite: 6]
        session['usuario_login'] = form.usuario.data
        
        # Redireciona para a nova tela de "Dados do acesso" (Padrão PRG)[cite: 6]
        return redirect(url_for('acesso'))
        
    return render_template('login.html', form=form, current_time=datetime.utcnow())

# NOVA ROTA: Dados do Acesso (Tela solicitada na imagem)
@app.route('/acesso')
def acesso():
    # Recupera o usuário salvo na sessão
    usuario = session.get('usuario_login')
    
    # Se alguém tentar acessar essa página sem ter logado, redireciona de volta pro login
    if not usuario:
        return redirect(url_for('login'))
        
    return render_template('acesso.html', usuario=usuario, current_time=datetime.utcnow())

if __name__ == '__main__':
    app.run(debug=True)