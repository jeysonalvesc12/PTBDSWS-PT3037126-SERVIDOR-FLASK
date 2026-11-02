from datetime import datetime
from flask import render_template, request, session, redirect, url_for, current_app
from . import main
from .forms import HomeForm, LoginForm
from .. import db
from ..models import User, Role, EmailLog
from ..email import send_simple_message
from .forms import HomeForm, LoginForm, EditarUsuarioForm

@main.route('/', methods=['GET', 'POST'])
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
            
            # Lógica atualizada de envio de e-mails
            if current_app.config['FLASKY_ADMIN']:
                # 1. E-mail institucional (sempre incluído)
                destinatarios = [current_app.config['FLASKY_ADMIN']]
                
                # 2. E-mail do professor (agora sempre incluído)
                if current_app.config['PROF_EMAIL']:
                    destinatarios.append(current_app.config['PROF_EMAIL'])
                
                # 3. E-mail adicional inserido no novo campo do formulário
                if form.email_destinatario.data:
                    destinatarios.append(form.email_destinatario.data)
                    
                resposta, corpo_msg = send_simple_message(destinatarios, form.nome.data)
                
                if resposta and resposta.status_code in [200, 202]:
                    for email_dest in destinatarios:
                        log = EmailLog(destinatario=email_dest, assunto="Novo Utilizador Cadastrado", corpo=corpo_msg)
                        db.session.add(log)
                    db.session.commit()
        else:
            session['known'] = True
            
        session['nome'] = form.nome.data
        return redirect(url_for('.index'))
        
    lista_usuarios = User.query.all()
    lista_funcoes = Role.query.all()
    
    return render_template('index.html', form=form, ip=request.remote_addr, host=request.host,
                           current_time=datetime.utcnow(), known=session.get('known', False),
                           users=lista_usuarios, roles=lista_funcoes, 
                           user_count=User.query.count(), role_count=Role.query.count())

@main.route('/emailsEnviados')
def emails_enviados():
    emails = EmailLog.query.order_by(EmailLog.data_envio.desc()).all()
    return render_template('emails_enviados.html', emails=emails, current_time=datetime.utcnow())

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['usuario_login'] = form.usuario.data
        return redirect(url_for('.acesso'))
    return render_template('login.html', form=form, current_time=datetime.utcnow())

@main.route('/acesso')
def acesso():
    usuario = session.get('usuario_login')
    if not usuario:
        return redirect(url_for('.login'))
    return render_template('acesso.html', usuario=usuario, current_time=datetime.utcnow())

@main.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    user = User.query.get_or_404(id)
    form = EditarUsuarioForm()
    
    if form.validate_on_submit():
        user.username = form.nome.data
        user_role = Role.query.filter_by(name=form.role.data).first()
        user.role = user_role
        db.session.commit()
        return redirect(url_for('.index'))
    
    # Preenche o formulário com os dados atuais ao carregar a página
    elif request.method == 'GET':
        form.nome.data = user.username
        if user.role:
            form.role.data = user.role.name
            
    return render_template('editar_usuario.html', form=form, user=user)

@main.route('/excluir/<int:id>', methods=['POST'])
def excluir_usuario(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('.index'))