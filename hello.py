import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Chave forte'

# --- CONFIGURAÇÕES ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['API_URL'] = os.environ.get('API_URL')
app.config['API_FROM'] = os.environ.get('API_FROM')
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['PROF_EMAIL'] = os.environ.get('PROF_EMAIL')

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app) 
migrate = Migrate(app, db) 

# --- FUNÇÃO DE E-MAIL ---
def send_simple_message(to_emails, novo_utilizador):
    headers = {
        "Authorization": f"Bearer {app.config['API_KEY']}",
        "Content-Type": "application/json"
    }
    
    texto_mensagem = f"Novo utilizador cadastrado: {novo_utilizador}\nDados do Aluno:\nNome: Jason Alves\nProntuário: PT3037126"
    
    personalizations = [{"to": [{"email": email}]} for email in to_emails]
    
    data = {
        "personalizations": personalizations,
        "from": {"email": app.config['API_FROM']},
        "subject": "Novo Utilizador Cadastrado",
        "content": [{"type": "text/plain", "value": texto_mensagem}]
    }
    
    try:
        resposta = requests.post(app.config['API_URL'], headers=headers, json=data)
        return resposta, texto_mensagem
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return None, texto_mensagem

# --- MODELOS DE DADOS ---
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

# NOVO MODELO: Tabela para persistir os e-mails enviados
class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    id = db.Column(db.Integer, primary_key=True)
    destinatario = db.Column(db.String(120), nullable=False)
    assunto = db.Column(db.String(120), nullable=False)
    corpo = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, EmailLog=EmailLog)

# --- FORMULÁRIOS ---
class HomeForm(FlaskForm):
    nome = StringField('What is your name?', validators=[DataRequired()])
    role = SelectField('Role?:', choices=[('Administrator', 'Administrator'), ('Moderator', 'Moderator'), ('User', 'User')])
    enviar_email_prof = BooleanField('Enviar e-mail para flaskaulasweb@zohomail.com')
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    usuario = StringField('', render_kw={"placeholder": "Usuário ou e-mail"}, validators=[DataRequired()])
    senha = PasswordField('', render_kw={"placeholder": "Informe a sua senha"}, validators=[DataRequired()])
    submit = SubmitField('Enviar')

# --- ROTAS ---
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
            
            if app.config['FLASKY_ADMIN']:
                destinatarios = [app.config['FLASKY_ADMIN']]
                if form.enviar_email_prof.data and app.config['PROF_EMAIL']:
                    destinatarios.append(app.config['PROF_EMAIL'])
                    
                resposta, corpo_msg = send_simple_message(destinatarios, form.nome.data)
                
                # NOVA LÓGICA: Se a API aceitar o envio, grava os dados na tabela EmailLog[cite: 28]
                if resposta and resposta.status_code in [200, 202]:
                    for email_dest in destinatarios:
                        log = EmailLog(destinatario=email_dest, assunto="Novo Utilizador Cadastrado", corpo=corpo_msg)
                        db.session.add(log)
                    db.session.commit()
        else:
            session['known'] = True
            
        session['nome'] = form.nome.data
        return redirect(url_for('index'))
        
    lista_usuarios = User.query.all()
    lista_funcoes = Role.query.all()
    
    return render_template('index.html', form=form, ip=request.remote_addr, host=request.host,
                           current_time=datetime.utcnow(), known=session.get('known', False),
                           users=lista_usuarios, roles=lista_funcoes, 
                           user_count=User.query.count(), role_count=Role.query.count())

# NOVA ROTA: Listar os e-mails persistidos no banco de dados[cite: 28]
@app.route('/emailsEnviados')
def emails_enviados():
    # Busca todos os e-mails ordenados do mais recente para o mais antigo
    emails = EmailLog.query.order_by(EmailLog.data_envio.desc()).all()
    return render_template('emails_enviados.html', emails=emails, current_time=datetime.utcnow())

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