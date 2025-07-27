from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Optional

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')


class RegisterForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    nome_completo = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    confirm = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    profile = SelectField('Perfil', choices=[('curioso', 'Curioso'), ('aluno', 'Aluno'), ('funcionario', 'Funcionário')])
    matricula = StringField('Matrícula', validators=[Optional()])  # Só exigido para aluno ou funcionário
    submit = SubmitField('Cadastrar')

class CriarMatriculaForm(FlaskForm):
    nome_completo = StringField('Nome Completo', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    tipo = SelectField('Tipo', choices=[('aluno', 'Aluno'), ('funcionario', 'Funcionário')], validators=[DataRequired()])
    submit = SubmitField('Gerar Matrícula')
