from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired

class HomeForm(FlaskForm):
    nome = StringField('What is your name?', validators=[DataRequired()])
    role = SelectField('Role?:', choices=[('Administrator', 'Administrator'), ('Moderator', 'Moderator'), ('User', 'User')])
    
    # NOVO: Campo para inclusão de endereço de e-mail (substitui o antigo BooleanField)
    email_destinatario = StringField('Endereço de e-mail para recebimento')
    
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    usuario = StringField('', render_kw={"placeholder": "Usuário ou e-mail"}, validators=[DataRequired()])
    senha = PasswordField('', render_kw={"placeholder": "Informe a sua senha"}, validators=[DataRequired()])
    submit = SubmitField('Enviar')