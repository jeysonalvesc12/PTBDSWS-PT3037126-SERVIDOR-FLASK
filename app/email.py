import requests
from flask import current_app, render_template

# 1. NOVA FUNÇÃO: Exigida pelo módulo de Autenticação da Aula 090
def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    
    # O módulo auth passa um template HTML específico (ex: 'auth/email/confirm')
    html_body = render_template(template + '.html', **kwargs)
    
    resposta = requests.post(
        app.config['API_URL'],
        auth=("api", app.config['API_KEY']),
        data={
            "from": app.config['API_FROM'],
            "to": to,
            "subject": app.config.get('FLASKY_MAIL_SUBJECT_PREFIX', '[Aplicação]') + ' ' + subject,
            "html": html_body
        }
    )
    return resposta

# 2. FUNÇÃO ANTIGA: Mantida para não quebrar a rota index do main
def send_simple_message(to_list, nome):
    app = current_app._get_current_object()
    
    html_body = f"<p>Novo utilizador cadastrado: {nome}</p>"
    
    resposta = requests.post(
        app.config['API_URL'],
        auth=("api", app.config['API_KEY']),
        data={
            "from": app.config['API_FROM'],
            "to": to_list,
            "subject": app.config.get('FLASKY_MAIL_SUBJECT_PREFIX', '[Aplicação]') + " Novo Cadastro",
            "html": html_body
        }
    )
    return resposta, html_body