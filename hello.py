import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Carrega as variáveis de ambiente do ficheiro .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Chave forte'

# --- 1. CONFIGURAÇÃO DO BANCO DE DADOS E SENDGRID ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Carrega as chaves da API de e-mail a partir do .env
app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['API_URL'] = os.environ.get('API_URL')
app.config['API_FROM'] = os.environ.get('API_FROM')
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['PROF_EMAIL'] = os.environ.get('PROF_EMAIL')

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app) 
migrate = Migrate(app, db) 

# --- 2. FUNÇÃO DE ENVIO DE E-MAIL (SENDGRID) ---
def send_simple_message(to_emails, novo_utilizador):
    headers = {
        "Authorization": f"Bearer {app.config['API_KEY']}",
        "Content-Type": "application/json"
    }
    
    texto_mensagem = f"""
    Novo utilizador cadastrado: {novo_utilizador}
    
    Dados do Aluno:
    Nome: Jason Alves
    Prontuário: PT3037126
    """
    
    personalizations = [{"to": [{"email": email}]} for email in to_emails]
    
    data = {
        "personalizations": personalizations,
        "from": {"email": app.config['API_FROM']},
        "subject": "Novo Utilizador Cadastrado",
        "content": [
            {
                "type": "text/plain",
                "value": texto_mensagem
            }
        ]
    }
    
    try:
        resposta = requests.post(app.config['API_URL'], headers=headers, json=data)
        return resposta
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return None

# --- 3. DEFINIÇÃO DOS MODELOS DE DADOS ---
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

# --- 4. INTEGRAÇÃO COM O SHELL PYTHON ---
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

# --- 5. FORMULÁRIOS ---
class HomeForm(FlaskForm):
    nome = StringField('What is your name?', validators=[DataRequired()])
    role = SelectField('Role?:', 
                       choices=[('Administrator', 'Administrator'), 
                                ('Moderator', 'Moderator'), 
                                ('User', 'User')])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    usuario = StringField('', render_kw={"placeholder": "Usuário ou e-mail"}, validators=[DataRequired()])
    senha = PasswordField('', render_kw={"placeholder": "Informe a sua senha"}, validators=[DataRequired()])
    submit = SubmitField('Enviar')

# --- 6. TRATAMENTO DE ERROS ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# --- 7. ROTAS ---
@app.route('/', methods=['GET', 'POST'])
def index():
    form = HomeForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.nome.data).first()
        
        if user is None: 
            user_role = Role.query.filter_by(name=form.role.data).first()
            user = User(username=form.nome.data, role=user_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            
            # --- DISPARO DE E-MAIL APÓS GRAVAR NO BANCO ---
            if app.config['FLASKY_ADMIN'] and app.config['PROF_EMAIL']:
                destinatarios = [app.config['FLASKY_ADMIN'], app.config['PROF_EMAIL']]
                send_simple_message(destinatarios, form.nome.data)
                
        else:
            session['known'] = True
            
        session['nome'] = form.nome.data
        return redirect(url_for('index'))
        
    # Consultas para as listas e contadores
    lista_usuarios = User.query.all()
    lista_funcoes = Role.query.all()
    total_usuarios = User.query.count()
    total_funcoes = Role.query.count()
    
    # Captura de IP e Host
    ip = request.remote_addr
    host = request.host
    
    return render_template('index.html', 
                           form=form, 
                           ip=ip,
                           host=host,
                           current_time=datetime.utcnow(), 
                           known=session.get('known', False),
                           users=lista_usuarios,
                           roles=lista_funcoes,
                           user_count=total_usuarios,
                           role_count=total_funcoes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        session['usuario_login'] = form.usuario.data
        return redirect(url_for('acesso'))
        
    return render_template('login.html', form=form, current_time=datetime.utcnow())

@app.route('/acesso')
def acesso():
    usuario = session.get('usuario_login')
    
    if not usuario:
        return redirect(url_for('login'))
        
    return render_template('acesso.html', usuario=usuario, current_time=datetime.utcnow())

if __name__ == '__main__':
    app.run(debug=True)