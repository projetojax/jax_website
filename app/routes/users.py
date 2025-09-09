from flask import Blueprint, render_template, Flask, redirect, request, session, flash, url_for
from datetime import datetime
from app.auth.utils import (
    detalhar_usuario,
    listar_usuarios,
    atualizar_usuario,
    remover_usuario,
    criar_conta
)

user_routes = Blueprint("users", __name__)
current_year = datetime.now().year

from flask import session
from datetime import timedelta

@user_routes.route('/perfil', methods=['GET', 'POST'])
def perfil():
    user_id = session['usuario']['id']

    if request.method == 'POST':
        username = request.form.get('username')
        nome_completo = request.form.get('nome_completo')
        email = request.form.get('email')
        password = request.form.get('password')  # opcional
        profile = detalhar_usuario(user_id).get('profile', 'curioso')  # Pega o perfil atual
        sucesso, mensagem = atualizar_usuario(user_id, username, nome_completo, email, password, profile)

        if sucesso:
            flash(mensagem, 'success')
            session['usuario']['username'] = username  # atualiza sessão
            session['usuario']['email'] = email
        else:
            flash(mensagem, 'danger')

    usuario = detalhar_usuario(user_id)
    user_name = session['usuario']
    return render_template('users/perfil.html', usuario=usuario, year=current_year, current_user=user_name)


@user_routes.route('/perfil/remover', methods=['POST'])
def remover_proprio_usuario():
    user_id = session['usuario']['id']
    sucesso, mensagem = remover_usuario(user_id)

    if sucesso:
        flash("Conta excluída com sucesso.", "info")
        session.clear()
        return render_template('public/home.html', title='Home', year=current_year)
    else:
        flash(mensagem, "danger")
        return redirect(url_for('perfil'))


@user_routes.route('/usuarios', methods=['GET'])
def usuarios():

    usuarios = listar_usuarios()
    usuario = session['usuario']
    return render_template('users/usuarios.html', usuarios=usuarios, year=current_year, current_user=usuario)


@user_routes.route('/<int:user_id>/editar', methods=['GET', 'POST'])
def editar(user_id):

    if request.method == 'POST':
        usuarios = listar_usuarios()
        usuario = session['usuario']
        username = request.form.get('username')
        nome_completo = request.form.get('nome_completo')
        email = request.form.get('email')
        password = request.form.get('password')  # opcional
        profile = request.form.get('profile')

        sucesso, mensagem = atualizar_usuario(user_id, username, nome_completo, email, password, profile)

        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'danger')

        return render_template('users/usuarios.html', usuarios=usuarios, year=current_year, current_user=usuario)

    usuario = detalhar_usuario(user_id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return render_template('users/usuarios.html', usuarios=usuarios, year=current_year, current_user=usuario)

    return render_template('users/editar_usuario.html', usuario=usuario)


@user_routes.route('/<int:user_id>/remover', methods=['POST'])
def remover(user_id):

    usuarios = listar_usuarios()
    usuario = session['usuario']

    sucesso, mensagem = remover_usuario(user_id)
    flash(mensagem, "success" if sucesso else "danger")
    return render_template('users/usuarios.html', usuarios=usuarios, year=current_year, current_user=usuario)

@user_routes.route('/usuarios/novo', methods=['GET', 'POST'])
def novo_usuario():
    if session.get("usuario", {}).get("profile") != "admin":
        flash("Acesso restrito.", "danger")
        return redirect(url_for('public.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        nome_completo = request.form.get('nome_completo')
        email = request.form.get('email')
        profile = request.form.get('profile')

        # senha genérica (usuário altera depois no "Meu Perfil")
        senha_generica = "123456"
        sucesso, mensagem = criar_conta(username, nome_completo, email, senha_generica, profile)

        if sucesso:
            flash(f"{mensagem} Senha temporária: {senha_generica}", "success")
            return redirect(url_for('users.usuarios'))
        else:
            flash(mensagem, "danger")

    return render_template('users/novo_usuario.html')
