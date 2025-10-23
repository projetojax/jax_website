from flask import Blueprint, render_template, redirect, request, flash, url_for
from flask_login import current_user, login_required
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

@user_routes.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        username = request.form.get('username')
        nome_completo = request.form.get('nome_completo')
        email = request.form.get('email')
        password = request.form.get('password')  # opcional
        
        sucesso, mensagem = atualizar_usuario(
            current_user.id, 
            username, 
            nome_completo, 
            email, 
            password, 
            current_user.profile  # Mantém o perfil atual
        )

        if sucesso:
            flash(mensagem, 'success')
            # A sessão é automaticamente atualizada pelo Flask-Login
        else:
            flash(mensagem, 'danger')

    usuario = detalhar_usuario(current_user.id)
    return render_template('users/perfil.html', usuario=usuario, year=current_year, current_user=current_user)

@user_routes.route('/perfil/remover', methods=['POST'])
@login_required
def remover_proprio_usuario():
    sucesso, mensagem = remover_usuario(current_user.id)

    if sucesso:
        from flask_login import logout_user
        logout_user()
        flash("Conta excluída com sucesso.", "info")
        return redirect(url_for('public.home'))
    else:
        flash(mensagem, "danger")
        return redirect(url_for('users.perfil'))

@user_routes.route('/usuarios', methods=['GET'])
@login_required
def usuarios():
    if current_user.profile != 'admin':
        flash("Acesso restrito.", "danger")
        return redirect(url_for('public.home'))
    
    usuarios = listar_usuarios()
    return render_template('users/usuarios.html', usuarios=usuarios, year=current_year, current_user=current_user)

@user_routes.route('/<int:user_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(user_id):
    if current_user.profile != 'admin':
        flash("Acesso restrito.", "danger")
        return redirect(url_for('public.home'))

    if request.method == 'POST':
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

        return redirect(url_for('users.usuarios'))

    usuario = detalhar_usuario(user_id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for('users.usuarios'))

    return render_template('users/editar_usuario.html', usuario=usuario, year=current_year, current_user=current_user)

@user_routes.route('/<int:user_id>/remover', methods=['POST'])
@login_required
def remover(user_id):
    if current_user.profile != 'admin':
        flash("Acesso restrito.", "danger")
        return redirect(url_for('public.home'))

    # Impede que o admin se remova a si mesmo
    if user_id == current_user.id:
        flash("Você não pode remover sua própria conta.", "danger")
        return redirect(url_for('users.usuarios'))

    sucesso, mensagem = remover_usuario(user_id)
    flash(mensagem, "success" if sucesso else "danger")
    return redirect(url_for('users.usuarios'))

@user_routes.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
def novo_usuario():
    if current_user.profile != 'admin':
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

    return render_template('users/novo_usuario.html', year=current_year, current_user=current_user)
