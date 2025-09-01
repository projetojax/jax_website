from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from .forms import LoginForm, RegisterForm, CriarMatriculaForm
from .utils import realizar_login, realizar_logout, criar_conta, criar_matricula, validar_matricula, confirmar_matricula, gerar_matricula_personalizada, listar_matriculas, detalhar_usuario

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
            return redirect(url_for('public.home'))
        else:
            flash("Credenciais inválidas. Tente novamente.", "danger")
    return render_template('login.html', form=form, year=current_year)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        perfil = form.profile.data
        matricula = form.matricula.data.strip() if form.matricula.data else None

        if perfil in ["aluno", "funcionario"]:
            if not validar_matricula(matricula, perfil):
                flash("Matrícula inválida ou não encontrada para esse perfil.", "danger")
                return render_template('register.html', form=form, year=current_year)

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

    return render_template('register.html', form=form, year=current_year)

@auth.route('/logout')
def logout():
    if 'usuario' in session:
        nome = session['usuario'].get('username', 'usuário')
        realizar_logout(session)
        flash(f"Logout realizado com sucesso, {nome}.", "info")
    return redirect(url_for('public.home'))

@auth.route('/matricula', methods=['POST'])
def criar_matricula_api():
    if session.get("usuario", {}).get("profile") != "admin":
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
            return render_template('admin_matriculas.html', form=form, matriculas=registros, year=current_year, current_user=usuario)
        else:
            flash(mensagem, "danger")

    registros = listar_matriculas()
    usuario = session['usuario']
    return render_template('admin_matriculas.html', form=form, matriculas=registros, year=current_year, current_user=usuario)

@auth.route('/admin/matriculas', methods=['GET', 'POST'])
def gerenciar_matriculas():
    if session.get("usuario", {}).get("profile") != "admin":
        flash("Acesso restrito.", "danger")
        return redirect(url_for('public.home'))

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
            usuario = session['usuario']
            return render_template('admin_matriculas.html', form=form, matriculas=registros, year=current_year, current_user=usuario)
        else:
            flash(mensagem, "danger")
    else:
        flash("Erro ao validar o formulário. Verifique os dados inseridos.", "danger")

    registros = listar_matriculas()
    usuario = session['usuario']
    return render_template('admin_matriculas.html', form=form, matriculas=registros, year=current_year, current_user=usuario)
