from flask import Blueprint, render_template, Flask, redirect, request, session, flash, url_for
from datetime import datetime
from .auth.utils import (
    detalhar_usuario,
    listar_usuarios,
    atualizar_usuario,
    remover_usuario
)

main = Blueprint("main", __name__)
current_year = datetime.now().year

from flask import session
from datetime import timedelta

@main.before_request
def refresh_session():
    session.permanent = True
    main.permanent_session_lifetime = timedelta(minutes=30)

@main.route("/<path:path>")
def jax_services(path):
    try:
        if '.html' not in path and 'sitemap' not in path:
            return render_template(f'{path}.html', title=path.capitalize(), year=current_year)
        if 'sitemap' in path:
            return render_template('sitemap.xml', title='Sitemap', year=current_year)
        else:
            return render_template(f'{path}', title=path.capitalize(), year=current_year)
    except Exception as e:
        if '.html' in str(e):
            return render_template('error.html', title="ERROR", error=f"Página ( {str(e)} ) não encontrada")
        return render_template('error.html', title="ERROR", error=str(e))

@main.route('/')
@main.route('/home')
def home():

    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('home.html', title='Home', year=current_year, current_user=usuario)

    return render_template('home.html', title='Home', year=current_year)

@main.route('/google-site-verification=<token>.html')
def google_verification():
    return render_template('google-site-verification=OoaVt6jNPKKCO9AiGsIeFX3_muqcrkHbLgRui2LYSRg.html', title='Google Site Verification', year=current_year)

@main.route('/sitemap')
def sitemap():
    return render_template('sitemap.xml', title='Sitemap', year=current_year)

@main.route('/sobre')
def sobre():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('sobre.html', title='Sobre', year=current_year, current_user=usuario)
    return render_template('sobre.html', title='Sobre', year=current_year)

@main.route('/galeria')
def galeria():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('galeria.html', title='Galeria', year=current_year, current_user=usuario)
    return render_template('galeria.html', title='Galeria', year=current_year)

@main.route('/contato')
def contato():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('contato.html', title='Contato', year=current_year, current_user=usuario)
    return render_template('contato.html', title='Contato', year=current_year)

@main.route('/historia')
def historia():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('historia.html', title='História', year=current_year, current_user=usuario)
    return render_template('historia.html', title='História', year=current_year)

@main.route('/funcionalidades')
def funcionalidades():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('funcionalidades.html', title='Funcionalidades', year=current_year, current_user=usuario)
    return render_template('funcionalidades.html', title='Funcionalidades', year=current_year)

@main.route('/documento')
def documento():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('documento.html', title='Documentacao', year=current_year, current_user=usuario) 
    return render_template('documento.html', title='Documentacao', year=current_year)

@main.route('/jax_jornada')
def jax_jornada():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('jax_jornada.html', title='Jornada', year=current_year, current_user=usuario)
    return render_template('jax_jornada.html', title='Jornada', year=current_year)

@main.route("/jaxresume")
def jaxresume():
    from .utils import load_jaxresume

    if 'usuario' in session:
        usuario = session['usuario']
        main.permanent_session_lifetime = timedelta(minutes=30)
        return render_template("jaxresume.html", temas=load_jaxresume(main)[0], year=current_year, current_user=usuario)
    return render_template("jaxresume.html", temas=load_jaxresume(main)[0], year=current_year)

@main.route("/jaxresume/<tema>")
def temas(tema):
    from .utils import load_jaxresume
    tema = str(tema).capitalize()
    posts = load_jaxresume(main)[1][tema]
    if posts is None:
        return render_template("error.html", title="ERROR", error="Tema não encontrado")
    filtered_posts = [post for post in posts if post['theme'].lower() == tema.lower()]
    if len(filtered_posts) == 0:
        return render_template("error.html", title="ERROR", error="Tema não encontrado", year=current_year)

    if 'usuario' in session:
        usuario = session['usuario']
        return render_template("lista_posts.html", posts=filtered_posts, tema=tema, year=current_year, current_user=usuario)
    return render_template("lista_posts.html", posts=filtered_posts, tema=tema, year=current_year)

@main.route("/jaxresume/post/<int:post_id>")
def post(post_id):
    from .utils import load_jaxresume
    post_id = int(post_id)
    posts = load_jaxresume(main)[2][post_id]
    if posts is None:
        return render_template("error.html", title="ERROR", error="Post não encontrado", year=current_year)
    if post is None:
        return render_template("error.html", title="ERROR", error="Post não encontrado", year=current_year)

    if 'usuario' in session:
        usuario = session['usuario']
        return render_template("post_completo.html", post=posts, year=current_year, current_user=usuario)

    return render_template("post_completo.html", post=posts, year=current_year)

@main.route("/jaxresume/post/<post_id>/add_comment", methods=["POST"])
def add_comment_jaxresume(post_id):
    from flask import request
    from .utils import add_comment, load_jaxresume
    author = request.form.get("author")
    text = request.form.get("text")

    if not author or not text:
        author = "anonimo"

    try:
        _ = add_comment(post_id, 'jax_resume', author, text, main)
        return post(post_id)
    except FileNotFoundError as e:
        return render_template("error.html", title="ERROR", error=str(e), year=current_year)

@main.route('/jaxaulas')
def jaxaulas():

    from .utils import load_jaxaulas

    tutorials = load_jaxaulas(main)
    themes = {tutorial['theme'] for tutorial in tutorials}  # Obter temas únicos

    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('jaxaulas.html', themes=themes, year=current_year, current_user=usuario)

    return render_template('jaxaulas.html', themes=themes, year=current_year)

@main.route('/jaxaulas/<theme>')
def jaxaulas_theme(theme):

    from .utils import load_jaxaulas

    tutorials = [t for t in load_jaxaulas(main) if t['theme'].lower() == theme.lower()]
    if not tutorials:
        return render_template("error.html", title="ERROR", error="Tutorial nao existe", year=current_year), 404

    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('jaxaulas_topicos.html', theme=theme, tutorials=tutorials, year=current_year, current_user=usuario)

    return render_template('jaxaulas_topicos.html', theme=theme, tutorials=tutorials, year=current_year)

@main.route('/jaxaulas/watch/<int:tutorial_id>')
def jaxaulas_watch(tutorial_id):

    from .utils import load_jaxaulas
    tutorials = load_jaxaulas(main)
    tutorial = next((t for t in tutorials if t['id'] == tutorial_id), None)
    if not tutorial:
        return render_template("error.html", title="ERROR", error="Tutorial nao existe", year=current_year), 404

    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('jaxaulas_assistir.html', tutorial=tutorial, year=current_year, current_user=usuario)

    return render_template('jaxaulas_assistir.html', tutorial=tutorial, year=current_year)

@main.route("/jaxaulas/watch/<int:tutorial_id>/add_comment", methods=["POST"])
def add_comment_jaxaulas(tutorial_id):
    from flask import request
    from .utils import load_jaxaulas, add_comment
    tutorials = load_jaxaulas(main)
    tutorial = next((t for t in tutorials if t['id'] == tutorial_id), None)
    if not tutorial:
        return render_template("error.html", title="ERROR", error="Tutorial nao existe", year=current_year), 404

    author = request.form.get("author")
    text = request.form.get("text")

    if not author or not text:
        author = "anonimo"

    try:
        _ = add_comment(tutorial_id, 'jax_aulas', author, text, main)
        return jaxaulas_watch(tutorial_id)
    except FileNotFoundError as e:
        return render_template("error.html", title="ERROR", error=str(e), year=current_year)

@main.route('/perfil', methods=['GET', 'POST'])
def perfil():
    user_id = session['usuario']['id']

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')  # opcional
        sucesso, mensagem = atualizar_usuario(user_id, username, email, password)

        if sucesso:
            flash(mensagem, 'success')
            session['usuario']['username'] = username  # atualiza sessão
            session['usuario']['email'] = email
        else:
            flash(mensagem, 'danger')

    usuario = detalhar_usuario(user_id)
    user_name = session['usuario']
    return render_template('perfil.html', usuario=usuario, year=current_year, current_user=user_name)


@main.route('/perfil/remover', methods=['POST'])
def remover_proprio_usuario():
    user_id = session['usuario']['id']
    sucesso, mensagem = remover_usuario(user_id)

    if sucesso:
        flash("Conta excluída com sucesso.", "info")
        session.clear()
        return render_template('home.html', title='Home', year=current_year)
    else:
        flash(mensagem, "danger")
        return redirect(url_for('perfil'))


@main.route('/usuarios', methods=['GET'])
def usuarios():

    usuarios = listar_usuarios()
    usuario = session['usuario']
    return render_template('usuarios.html', usuarios=usuarios, year=current_year, current_user=usuario)


@main.route('/<int:user_id>/editar', methods=['GET', 'POST'])
def editar(user_id):

    if request.method == 'POST':
        usuarios = listar_usuarios()
        usuario = session['usuario']
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')  # opcional
        profile = request.form.get('profile')

        sucesso, mensagem = atualizar_usuario(user_id, username, email, password, profile)

        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'danger')

        return render_template('usuarios.html', usuarios=usuarios, year=current_year, current_user=usuario)

    usuario = detalhar_usuario(user_id)
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return render_template('usuarios.html', usuarios=usuarios, year=current_year, current_user=usuario)

    return render_template('editar.html', usuario=usuario)


@main.route('/<int:user_id>/remover', methods=['POST'])
def remover(user_id):

    usuarios = listar_usuarios()
    usuario = session['usuario']

    sucesso, mensagem = remover_usuario(user_id)
    flash(mensagem, "success" if sucesso else "danger")
    return render_template('usuarios.html', usuarios=usuarios, year=current_year, current_user=usuario)

