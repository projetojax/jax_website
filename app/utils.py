from flask_login import LoginManager
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

root_path = os.path.dirname(os.path.abspath(__file__))

def usuario_tem_acesso(usuario, post):
    """
    Retorna True se o usuário tiver acesso ao post, conforme a visibilidade.
    """
    vis = post.get("visibility", "aberta")

    if vis == "aberta":
        return True
    if not usuario or not usuario.is_authenticated:  # Corrigido aqui
        return False

    papel = usuario.profile.lower()  # Agora usa o profile do User object

    if vis == "fechada_nativa":
        return True
    if vis == "fechada_aluno":
        return papel in ["aluno", "admin", "funcionario"]
    if vis == "fechada_interna":
        return papel in ["admin", "funcionario"]

    return False


def create_app():
    from flask import Flask
    from app.routes.public import public_routes
    from app.routes.jax_resume import resume_routes
    from app.routes.jax_aulas import jax_aulas_routes
    from app.routes.users import user_routes
    from app.routes.avatar import avatar_routes
    from .models import User, db, init_avatar_tables  # 👈 adicione isso
    from config import Config
    from .auth.routes import auth

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(public_routes, url_prefix='')
    app.register_blueprint(resume_routes, url_prefix='')
    app.register_blueprint(jax_aulas_routes, url_prefix='')
    app.register_blueprint(user_routes, url_prefix='')
    app.register_blueprint(auth, url_prefix='')
    app.register_blueprint(avatar_routes, url_prefix='')

    # Cria as tabelas de usuário e avatar no banco
    with app.app_context():
        db.create_all()
        init_avatar_tables()  # 👈 agora cria as tabelas de avatar também!

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


# ======================================
# Funções auxiliares (mantidas iguais)
# ======================================

def load_jaxaulas(app):
    import json
    import os

    files_json = os.path.join(root_path, 'static', 'json', 'jax_aulas')
    tutorials = []

    for filename in os.listdir(files_json):
        if filename.startswith("tutorial_") and filename.endswith(".json"):
            with open(os.path.join(files_json, filename), "r", encoding='utf-8') as file:
                tutorials.append(json.load(file))
    return tutorials


def load_jaxresume(app):
    import os
    import json
    themes = set()
    summary_data = {}
    detailed_data = {}

    def format_content(content):
        paragraphs = content.split("\n\n")
        formatted = ""

        for paragraph in paragraphs:
            if paragraph.strip().startswith("Dicas Práticas"):
                formatted += f"<h3>{paragraph.strip()}</h3>"
            elif paragraph.strip().startswith("-"):
                items = paragraph.strip().split("\n")
                formatted += "<ul>"
                for item in items:
                    formatted += f"<li>{item[2:].strip()}</li><br>"
                formatted += "</ul>"
            else:
                formatted += f"<p>{paragraph.strip()}</p>"

        return formatted

    json_folder = os.path.join(root_path, 'static', 'json', 'jax_resume')

    for filename in os.listdir(json_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(json_folder, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                post = json.load(f)
                detailed_data[post['id']] = post
                themes.add(post['theme'])
                post['content'] = format_content(post['content'])

                if post['theme'] not in summary_data:
                    summary_data[post['theme']] = []
                summary_data[post['theme']].append({
                    'id': post['id'],
                    'image': post['image'],
                    'title': post['title'],
                    'subtitle': post['subtitle'],
                    'author': post['author'],
                    'theme': post['theme'],
                    'subtheme': post['subtheme'],
                    'date_published': post['date_published'],
                })

    return (sorted(list(themes)), summary_data, detailed_data)


def add_comment(post_id='', pasta_json='jax_resume', author='', text='', app=None):
    import os
    import json
    from datetime import datetime

    json_folder = os.path.join(root_path, 'static', 'json', pasta_json)
    if pasta_json == 'jax_resume':
        post_file = os.path.join(json_folder, f'post_{post_id}.json')
    elif pasta_json == 'jax_aulas':
        post_file = os.path.join(json_folder, f'tutorial_{post_id}.json')
    else:
        raise ValueError("Pasta de conjunto JSON inválida.")

    if not os.path.exists(post_file):
        raise FileNotFoundError(f"Post com ID {post_id} não encontrado.")

    with open(post_file, 'r', encoding='utf-8') as f:
        post_data = json.load(f)

    new_comment = {
        "author": author,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text
    }

    if "comments" not in post_data:
        post_data["comments"] = []

    post_data["comments"].append(new_comment)

    with open(post_file, 'w', encoding='utf-8') as f:
        json.dump(post_data, f, ensure_ascii=False, indent=4)

    return new_comment
