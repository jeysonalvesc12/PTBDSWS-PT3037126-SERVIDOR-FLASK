import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired
# Importando as bibliotecas de banco de dados
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Captura o diretório base do projeto para criar o banco na mesma pasta
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Chave forte'

# --- 1. CONFIGURAÇÃO DO BANCO DE DADOS ---

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
# Desativa o rastreamento de modificações para economizar memória[cite: 9]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização das extensões
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app) # Inicializa o banco de dados
migrate = Migrate(app, db) # Inicializa o gerenciador de migrações


# --- 2. DEFINIÇÃO DOS MODELOS DE DADOS 
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # Relacionamento: uma Role possui vários Users
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # Chave estrangeira que conecta com a tabela Roles
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


# --- 3. INTEGRAÇÃO COM O SHELL PYTHON 
# Carrega o contexto do banco de dados automaticamente ao usar 'flask shell'[cite: 9]
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)




class HomeForm(FlaskForm):
    nome = StringField('Informe o seu nome', validators=[DataRequired()])
    sobrenome = StringField('Informe o seu sobrenome:', validators=[DataRequired()])
    instituicao = StringField('Informe a sua Instituição de ensino:', validators=[DataRequired()])
    disciplina = SelectField('Informe a sua disciplina:', 
                             choices=[('DSWA5', 'DSWA5'), 
                                      ('DWBA4', 'DWBA4'), 
                                      ('Gestão de projetos', 'Gestão de projetos')])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    usuario = StringField('', render_kw={"placeholder": "Usuário ou e-mail"}, validators=[DataRequired()])
    senha = PasswordField('', render_kw={"placeholder": "Informe a sua senha"}, validators=[DataRequired()])
    submit = SubmitField('Enviar')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    form = HomeForm()
    
    if form.validate_on_submit():
        # Consulta no banco de dados se o nome já existe[cite: 9]
        user = User.query.filter_by(username=form.nome.data).first()
        
        if user is None: 
            # Usuário NOVO: Salva no banco de dados e marca known como False[cite: 9]
            user = User(username=form.nome.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            # Usuário EXISTENTE: Apenas marca known como True
            session['known'] = True
            
        # Continua salvando os dados do formulário na sessão do navegador
        session['nome'] = form.nome.data
        session['sobrenome'] = form.sobrenome.data
        session['instituicao'] = form.instituicao.data
        session['disciplina'] = form.disciplina.data
        
        return redirect(url_for('index'))
        
    ip = request.remote_addr
    host = request.host
    
    # ATENÇÃO AQUI: Agora estamos enviando a variável `known` para o HTML
    return render_template('index.html', form=form, ip=ip, host=host, current_time=datetime.utcnow(), known=session.get('known', False))

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