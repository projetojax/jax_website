from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    profile = SelectField('Perfil', choices=[('curioso', 'Curioso'), ('aluno', 'Aluno'), ('funcionario', 'Funcionário')])
    submit = SubmitField('Cadastrar')
