from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired

class HomeForm(FlaskForm):
    nome = StringField('What is your name?', validators=[DataRequired()])
    role = SelectField('Role?:', choices=[('Administrator', 'Administrator'), ('Moderator', 'Moderator'), ('User', 'User')])
    enviar_email_prof = BooleanField('Enviar e-mail para flaskaulasweb@zohomail.com')
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    usuario = StringField('', render_kw={"placeholder": "Usuário ou e-mail"}, validators=[DataRequired()])
    senha = PasswordField('', render_kw={"placeholder": "Informe a sua senha"}, validators=[DataRequired()])
    submit = SubmitField('Enviar')