from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from .forms import LoginForm, RegisterForm, CriarMatriculaForm
from .utils import realizar_login, realizar_logout, criar_conta, criar_matricula, validar_matricula, confirmar_matricula, gerar_matricula_personalizada, listar_matriculas, detalhar_usuario, excluir_matricula
from flask_login import login_user, logout_user, current_user, login_required
from ..models import User

auth = Blueprint('auth', __name__)
current_year = datetime.now().year

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        dados_usuario = realizar_login(form.username.data, form.password.data)
        if dados_usuario:
            # Busca o objeto User do SQLAlchemy
            user_obj = User.query.get(dados_usuario['id'])
            if user_obj:
                login_user(user_obj)  # Usa Flask-Login
                flash(f"Bem-vindo(a), {dados_usuario['username']}!", "success")
                return redirect(url_for('public.home'))
        flash("Credenciais inválidas. Tente novamente.", "danger")
    return render_template('auth/login.html', form=form, year=current_year)

@auth.route('/logout')
@login_required
def logout():
    nome = current_user.username
    logout_user()  # Usa Flask-Login
    flash(f"Logout realizado com sucesso, {nome}.", "info")
    return redirect(url_for('public.home'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        perfil = form.profile.data
        matricula = form.matricula.data.strip() if form.matricula.data else None

        if perfil in ["aluno", "funcionario"]:
            if not validar_matricula(matricula, perfil):
                flash("Matrícula inválida ou não encontrada para esse perfil.", "danger")
                return render_template('auth/register.html', form=form, year=current_year)

        sucesso, mensagem = criar_conta(
            username=form.username.data,
            nome_completo=form.nome_completo.data.strip(),
            email=form.email.data,
            password=form.password.data,
            profile=perfil
        )

        if sucesso:
            if perfil in ["aluno", "funcionario"]:
                confirmar_matricula(matricula)
            flash(mensagem, "success")
            return redirect(url_for('auth.login'))
        else:
            flash(mensagem, "danger")

    return render_template('auth/register.html', form=form, year=current_year)

@auth.route('/matricula', methods=['POST'])
def criar_matricula_api():
    if not current_user.is_authenticated or current_user.profile != "admin":
        flash("Acesso restrito.", "danger")
        return redirect(url_for('public.home'))

    

    form = CriarMatriculaForm()
    if form.validate_on_submit():
        nome = form.nome_completo.data.strip()
        email = form.email.data.strip()
        tipo = form.tipo.data.strip()

        print(f"Tipo de matrícula: {tipo}")
        print(f"Nome: {nome}, Email: {email}")

        numero_matricula = gerar_matricula_personalizada(tipo)
        print(f"Número de matrícula gerado: {numero_matricula}")
        sucesso, mensagem = criar_matricula(nome, email, numero_matricula)
        print(f"Resultado da criação: {sucesso}, Mensagem: {mensagem}")
        if sucesso:
            flash(f"{mensagem} Número: {numero_matricula}", "success")
            registros = listar_matriculas()
            return render_template('auth/admin_matriculas.html', form=form, matriculas=registros, year=current_year, current_user=current_user)
        else:
            flash(mensagem, "danger")

    registros = listar_matriculas()
    usuario = { "id": current_user.id, "username": current_user.username, "email": current_user.email, "profile": current_user.profile }
    return render_template('auth/admin_matriculas.html', form=form, matriculas=registros, year=current_year, current_user=current_user)

@auth.route('/admin/matriculas', methods=['GET', 'POST'])
@login_required
def gerenciar_matriculas():
    if not current_user.is_authenticated or current_user.profile != "admin":
        flash("Acesso restrito.", "danger")
        return redirect(url_for('public.home'))

    print(current_user)
    print(current_user.id)

    form = CriarMatriculaForm()
    form_valid = form.validate_on_submit()
    if form_valid:
        nome = form.nome_completo.data.strip()
        email = form.email.data.strip()
        tipo = form.tipo.data.strip()

        print(f"Tipo de matrícula: {tipo}")
        print(f"Nome: {nome}, Email: {email}")

        numero_matricula = gerar_matricula_personalizada(tipo)
        print(f"Número de matrícula gerado: {numero_matricula}")
        sucesso, mensagem = criar_matricula(nome, email, numero_matricula)
        print(f"Resultado da criação: {sucesso}, Mensagem: {mensagem}")
        if sucesso:
            flash(f"{mensagem} Número: {numero_matricula}", "success")
            registros = listar_matriculas()
            usuario = { "id": current_user.id, "username": current_user.username, "email": current_user.email, "profile": current_user.profile }
            return render_template('auth/admin_matriculas.html', form=form, matriculas=registros, year=current_year, current_user=current_user)
        else:
            flash(mensagem, "danger")
    else:
        flash("Erro ao validar o formulário. Verifique os dados inseridos.", "danger")

    registros = listar_matriculas()
    usuario = { "id": current_user.id, "username": current_user.username, "email": current_user.email, "profile": current_user.profile }
    return render_template('auth/admin_matriculas.html', form=form, matriculas=registros, year=current_year, current_user=current_user)

@auth.route('/admin/matriculas/delete/<int:matricula_id>', methods=['POST'])
def deletar_matricula(matricula_id):
    if not current_user.is_authenticated or current_user.profile != "admin":
        flash("Acesso restrito.", "danger")
        return redirect(url_for('public.home'))

    sucesso, mensagem = excluir_matricula(matricula_id)  # função que você vai criar no model/serviço
    if sucesso:
        flash("Matrícula excluída com sucesso.", "success")
    else:
        flash(mensagem or "Erro ao excluir matrícula.", "danger")

    return redirect(url_for('auth.gerenciar_matriculas'))

