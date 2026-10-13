from datetime import datetime
from flask import render_template, request, session, redirect, url_for, current_app
from . import main
from .forms import HomeForm, LoginForm
from .. import db
from ..models import User, Role, EmailLog
from ..email import send_simple_message

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
            
            # current_app é usado aqui dentro de rotas/blueprints
            if current_app.config['FLASKY_ADMIN']:
                destinatarios = [current_app.config['FLASKY_ADMIN']]
                if form.enviar_email_prof.data and current_app.config['PROF_EMAIL']:
                    destinatarios.append(current_app.config['PROF_EMAIL'])
                    
                resposta, corpo_msg = send_simple_message(destinatarios, form.nome.data)
                
                if resposta and resposta.status_code in [200, 202]:
                    for email_dest in destinatarios:
                        log = EmailLog(destinatario=email_dest, assunto="Novo Utilizador Cadastrado", corpo=corpo_msg)
                        db.session.add(log)
                    db.session.commit()
        else:
            session['known'] = True
            
        session['nome'] = form.nome.data
        
        # O ponto antes do index significa "a rota index dentro do mesmo blueprint"
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