from flask import Blueprint, render_template, Flask, send_from_directory

main = Blueprint("main", __name__)

@main.route('/google-site-verification=<token>.html')
def google_verification():
    return render_template('google-site-verification=OoaVt6jNPKKCO9AiGsIeFX3_muqcrkHbLgRui2LYSRg.html')

@main.route('/sitemap')
def sitemap():
    return render_template('sitemap.xml')

@main.route("/<path:path>")
def jax_services(path):
    try:
        if '.html' not in path and 'sitemap' not in path:
            return render_template(f'{path}.html')
        if 'sitemap' in path:
            return render_template('sitemap.xml')
        else:
            return render_template(f'{path}')
    except Exception as e:
        if '.html' in str(e):
            return render_template('error.html', title="ERROR", error=f"Página ( {str(e)} ) não encontrada")
        return render_template('error.html', title="ERROR", error=str(e))

@main.route('/')
def home():
    return render_template('home.html', title='Home')

@main.route('/sobre')
def sobre():
    return render_template('sobre.html', title='Sobre')

@main.route('/galeria')
def galeria():
    return render_template('galeria.html', title='Galeria')

@main.route('/contato')
def contato():
    return render_template('contato.html', title='Contato')

@main.route('/historia')
def historia():
    return render_template('historia.html', title='História')

@main.route('/funcionalidades')
def funcionalidades():
    return render_template('funcionalidades.html', title='Funcionalidades')

@main.route('/documento')
def documento():
    return render_template('documento.html', title='Documentacao')

@main.route("/jaxresume")
def jaxresume():
    from .utils import load_jaxresume
    return render_template("jaxresume.html", temas = load_jaxresume(main)[0])

@main.route("/jaxresume/<tema>")
def temas(tema):
    from .utils import load_jaxresume
    tema = str(tema).capitalize()
    posts = load_jaxresume(main)[1][tema]
    if posts is None:
        return render_template("error.html", title="ERROR", error="Tema não encontrado")
    filtered_posts = [post for post in posts if post['theme'].lower() == tema.lower()]
    if len(filtered_posts) == 0:
        return render_template("error.html", title="ERROR", error="Tema não encontrado")
    return render_template("lista_posts.html", posts=filtered_posts, tema=tema)

@main.route("/jaxresume/post/<int:post_id>")
def post(post_id):
    from .utils import load_jaxresume
    post_id = int(post_id)
    posts = load_jaxresume(main)[2][post_id]
    if posts is None:
        return render_template("error.html", title="ERROR", error="Post não encontrado")
    if post is None:
        return render_template("error.html", title="ERROR", error="Post não encontrado")
    return render_template("post_completo.html", post=posts)

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
        return render_template("error.html", title="ERROR", error=str(e))

@main.route('/jaxaulas')
def jaxaulas():

    from .utils import load_jaxaulas

    tutorials = load_jaxaulas(main)
    themes = {tutorial['theme'] for tutorial in tutorials}  # Obter temas únicos
    return render_template('jaxaulas.html', themes=themes)

@main.route('/jaxaulas/<theme>')
def jaxaulas_theme(theme):

    from .utils import load_jaxaulas

    tutorials = [t for t in load_jaxaulas(main) if t['theme'].lower() == theme.lower()]
    if not tutorials:
        return render_template("error.html", title="ERROR", error="Tutorial nao existe"), 404
    return render_template('jaxaulas_topicos.html', theme=theme, tutorials=tutorials)

@main.route('/jaxaulas/watch/<int:tutorial_id>')
def jaxaulas_watch(tutorial_id):

    from .utils import load_jaxaulas
    tutorials = load_jaxaulas(main)
    tutorial = next((t for t in tutorials if t['id'] == tutorial_id), None)
    if not tutorial:
        return render_template("error.html", title="ERROR", error="Tutorial nao existe"), 404
    
    return render_template('jaxaulas_assistir.html', tutorial=tutorial)

@main.route("/jaxaulas/watch/<int:tutorial_id>/add_comment", methods=["POST"])
def add_comment_jaxaulas(tutorial_id):
    from flask import request
    from .utils import load_jaxaulas, add_comment
    tutorials = load_jaxaulas(main)
    tutorial = next((t for t in tutorials if t['id'] == tutorial_id), None)
    if not tutorial:
        return render_template("error.html", title="ERROR", error="Tutorial nao existe"), 404

    author = request.form.get("author")
    text = request.form.get("text")

    if not author or not text:
        author = "anonimo"

    try:
        _ = add_comment(tutorial_id, 'jax_aulas', author, text, main)
        return jaxaulas_watch(tutorial_id)
    except FileNotFoundError as e:
        return render_template("error.html", title="ERROR", error=str(e))