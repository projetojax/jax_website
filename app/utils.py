from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    from flask import Flask
    from .routes import main
    from .models import User, db
    from config import Config
    from .auth.routes import auth
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(main)
    app.register_blueprint(auth)
    with app.app_context():
        db.create_all()
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    return app

def load_jaxaulas(app):
    import json
    import os

    files_json = os.path.join(app.root_path, 'static', 'json', 'jax_aulas')
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
        """Formata o conteúdo do post em HTML amigável."""
        paragraphs = content.split("\n\n")
        formatted = ""
        
        for paragraph in paragraphs:
            if paragraph.strip().startswith("Dicas Práticas"):
                formatted += f"<h3>{paragraph.strip()}</h3>"
            elif paragraph.strip().startswith("-"):
                items = paragraph.strip().split("\n")
                formatted += "<ul>"
                for item in items:
                    formatted += f"<li>{item[2:].strip()}</li><\br>" 
                formatted += "</ul>"
            else:
                formatted += f"<p>{paragraph.strip()}</p>"
        
        return formatted

    json_folder = os.path.join(app.root_path, 'static', 'json', 'jax_resume')  

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

def add_comment(post_id = '', pasta_json = 'jax_resume', author = '', text = '', app = None):

    import os
    import json
    from datetime import datetime

    json_folder = os.path.join(app.root_path, 'static', 'json', pasta_json)
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
