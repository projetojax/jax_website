from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from .forms import LoginForm, RegisterForm
from .utils import realizar_login, realizar_logout, criar_conta

auth = Blueprint('auth', __name__)
current_year = datetime.now().year

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        dados_usuario = realizar_login(form.username.data, form.password.data)
        if dados_usuario:
            session.permanent = True  # ativa controle por tempo
            session['usuario'] = dados_usuario  # guarda dados básicos
            flash(f"Bem-vindo(a), {dados_usuario['username']}!", "success")
            return redirect(url_for('main.home'))
        else:
            flash("Credenciais inválidas. Tente novamente.", "danger")
    return render_template('login.html', form=form, year=current_year)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        sucesso, mensagem = criar_conta(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            profile=form.profile.data
        )
        if sucesso:
            flash(mensagem, "success")
            return redirect(url_for('auth.login'))
        else:
            flash(mensagem, "danger")
    return render_template('register.html', form=form, year=current_year)


@auth.route('/logout')
def logout():
    if 'usuario' in session:
        nome = session['usuario'].get('username', 'usuário')
        realizar_logout(session)
        flash(f"Logout realizado com sucesso, {nome}.", "info")
    return redirect(url_for('main.home'))
