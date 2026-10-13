import requests
from flask import current_app

def send_simple_message(to_emails, novo_utilizador):
    headers = {
        "Authorization": f"Bearer {current_app.config['API_KEY']}",
        "Content-Type": "application/json"
    }
    
    texto_mensagem = f"Novo utilizador cadastrado: {novo_utilizador}\nDados do Aluno:\nNome: Jason Alves\nProntuário: PT3037126"
    
    personalizations = [{"to": [{"email": email}]} for email in to_emails]
    
    data = {
        "personalizations": personalizations,
        "from": {"email": current_app.config['API_FROM']},
        "subject": "Novo Utilizador Cadastrado",
        "content": [{"type": "text/plain", "value": texto_mensagem}]
    }
    
    try:
        resposta = requests.post(current_app.config['API_URL'], headers=headers, json=data)
        return resposta, texto_mensagem
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return None, texto_mensagem