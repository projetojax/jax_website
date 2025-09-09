from flask import Blueprint, render_template, redirect, request, session, flash, url_for
from datetime import datetime, timedelta
from app.utils import usuario_tem_acesso

resume_routes = Blueprint("resume", __name__)
current_year = datetime.now().year

@resume_routes.route("/jaxresume")
def jaxresume():
    from app.utils import load_jaxresume
    temas, _, _ = load_jaxresume(resume_routes)

    usuario = session.get("usuario")
    resume_routes.permanent_session_lifetime = timedelta(minutes=30)

    return render_template(
        "resumos/jaxresume.html",
        temas=temas,
        year=current_year,
        current_user=usuario
    )

@resume_routes.route("/jaxresume/<tema>")
def temas(tema):
    from app.utils import load_jaxresume
    tema = str(tema).capitalize()
    all_posts = load_jaxresume(resume_routes)[1].get(tema)

    if all_posts is None:
        return render_template("public/error.html", title="ERROR", error="Tema não encontrado", year=current_year)

    if 'usuario' in session:
        usuario = session['usuario']
    else:
        usuario = None

    # marcar posts com flag de acesso
    posts = []
    from app.uploads.jax_resumos import usuario_tem_acesso
    for post in all_posts:
        resumo = load_jaxresume(resume_routes)[2].get(post['id'])
        tem_acesso = usuario_tem_acesso(usuario, resumo) if resumo else False
        posts.append({**post, "sem_acesso": not tem_acesso})

    return render_template("resumos/lista_posts.html", posts=posts, tema=tema, year=current_year, current_user=usuario)

@resume_routes.route("/jaxresume/post/<int:post_id>")
def post(post_id):
    from app.utils import load_jaxresume
    from app.uploads.jax_resumos import usuario_tem_acesso

    resumo = load_jaxresume(resume_routes)[2].get(post_id)
    if resumo is None:
        return render_template("public/error.html", title="ERROR", error="Post não encontrado", year=current_year)

    usuario = session.get('usuario')
    if not usuario_tem_acesso(usuario, resumo):
        return render_template("error.html", title="ERROR", error="Você não tem permissão para acessar este resumo.", year=current_year)

    return render_template("resumos/post_completo.html", post=resumo, year=current_year, current_user=usuario)


@resume_routes.route("/jaxresume/post/<post_id>/add_comment", methods=["POST"])
def add_comment_jaxresume(post_id):
    from flask import request
    from app.utils import add_comment
    author = request.form.get("author")
    text = request.form.get("text")

    if not author or not text:
        author = "anonimo"

    try:
        _ = add_comment(post_id, 'jax_resume', author, text, resume_routes)
        return post(post_id)
    except FileNotFoundError as e:
        return render_template("public/error.html", title="ERROR", error=str(e), year=current_year)

@resume_routes.route('/jaxresume/novo', methods=['GET', 'POST'])
def novo_resumo():
    from app.uploads.jax_resumos import salvar_json
    if 'usuario' not in session:
        flash('Você precisa estar logado para criar um resumo.', 'warning')
        return render_template('auth/login.html')

    current_user = session['usuario']
    post = None

    if request.method == 'POST':
        try:
            novo_id = salvar_json(request.form, request.files, current_user['username'])
            flash(f'Resumo criado com sucesso! ID: {novo_id}', 'success')
        except Exception as e:
            flash(f'Ocorreu um erro ao salvar o resumo: {e}', 'danger')

    return render_template('resumos/editar_resumo.html', title="Novo Resumo", year=current_year, current_user=current_user, post=post)

@resume_routes.route('/jaxresume/lista')
def lista_resumos():
    from app.uploads.jax_resumos import listar_resumos
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    resumos = listar_resumos()
    return render_template('resumos/lista_resumos.html', resumos=resumos, year=current_year, current_user=session['usuario'])


@resume_routes.route('/jaxresume/editar/<int:post_id>', methods=['GET', 'POST'])
def editar_resumo(post_id):
    from app.utils import load_jaxresume
    if 'usuario' not in session:
        flash('Você precisa estar logado para editar.', 'warning')
        return render_template('auth/login.html')

    from app.uploads.jax_resumos import salvar_json, resumo_novo_id

    current_user = session['usuario']
    post = load_jaxresume(resume_routes)[2][post_id]

    if request.method == 'POST':
        try:
            print("Requisicao post recebida")
            print(request.form, request.files, current_user['username'])
            salvar_json(request.form, request.files, current_user['username'], post_id=post_id)
            flash('Resumo atualizado com sucesso!', 'success')
        except Exception as e:
            print("Erro ao atualizar resumo:", e)
            flash(f'Ocorreu um erro ao atualizar: {e}', 'danger')

    return render_template('resumos/editar_resumo.html', title="Editar Resumo", year=current_year, current_user=current_user, post=post)

@resume_routes.route('/jaxresume/remover/<int:id>', methods=['POST'])
def remover_resumo(id):
    from app.uploads.jax_resumos import remover_resumo_por_id, listar_resumos
    resumos = listar_resumos()

    if 'usuario' not in session:
        return redirect(url_for('auth.login'))

    try:
        remover_resumo_por_id(id)
        flash("Resumo removido com sucesso.", "success")
    except Exception as e:
        flash(f"Erro ao remover resumo: {e}", "danger")

    return render_template('resumos/lista_resumos.html', resumos=resumos, year=current_year, current_user=session['usuario'])
