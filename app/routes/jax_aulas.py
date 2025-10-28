from flask import Blueprint, render_template, Flask, redirect, request, session, flash, url_for
from datetime import datetime

jax_aulas_routes = Blueprint("aulas", __name__)
current_year = datetime.now().year

from flask import session
from datetime import timedelta
from flask_login import current_user


@jax_aulas_routes.route('/jaxaulas')
def jaxaulas():

    from app.utils import load_jaxaulas

    tutorials = load_jaxaulas(jax_aulas_routes)
    themes = {tutorial['theme'] for tutorial in tutorials}  # Obter temas únicos

    if current_user.is_authenticated:
        usuario = { "id": current_user.id, "username": current_user.username, "email": current_user.email, "profile": current_user.profile }
        return render_template('aulas/jaxaulas.html', themes=themes, year=current_year, current_user=usuario)

    return render_template('aulas/jaxaulas.html', themes=themes, year=current_year)

@jax_aulas_routes.route('/jaxaulas/<theme>')
def jaxaulas_theme(theme):

    from app.utils import load_jaxaulas

    tutorials = [t for t in load_jaxaulas(jax_aulas_routes) if t['theme'].lower() == theme.lower()]
    if not tutorials:
        return render_template("public/error.html", title="ERROR", error="Tutorial nao existe", year=current_year), 404

    if current_user.is_authenticated:
        usuario = { "id": current_user.id, "username": current_user.username, "email": current_user.email, "profile": current_user.profile }
        return render_template('aulas/jaxaulas_topicos.html', theme=theme, tutorials=tutorials, year=current_year, current_user=usuario)

    return render_template('aulas/jaxaulas_topicos.html', theme=theme, tutorials=tutorials, year=current_year)

@jax_aulas_routes.route('/jaxaulas/watch/<int:tutorial_id>')
def jaxaulas_watch(tutorial_id):

    from app.utils import load_jaxaulas
    tutorials = load_jaxaulas(jax_aulas_routes)
    tutorial = next((t for t in tutorials if t['id'] == tutorial_id), None)
    if not tutorial:
        return render_template("error.html", title="ERROR", error="Tutorial nao existe", year=current_year), 404

    if current_user.is_authenticated:
        usuario = { "id": current_user.id, "username": current_user.username, "email": current_user.email, "profile": current_user.profile }
        return render_template('aulas/jaxaulas_assistir.html', tutorial=tutorial, year=current_year, current_user=usuario)

    return render_template('aulas/jaxaulas_assistir.html', tutorial=tutorial, year=current_year)

@jax_aulas_routes.route("/jaxaulas/watch/<int:tutorial_id>/add_comment", methods=["POST"])
def add_comment_jaxaulas(tutorial_id):
    from flask import request
    from app.utils import load_jaxaulas, add_comment
    tutorials = load_jaxaulas(jax_aulas_routes)
    tutorial = next((t for t in tutorials if t['id'] == tutorial_id), None)
    if not tutorial:
        return render_template("public/error.html", title="ERROR", error="Tutorial nao existe", year=current_year), 404

    author = request.form.get("author")
    text = request.form.get("text")

    if not author or not text:
        author = "anonimo"

    try:
        _ = add_comment(tutorial_id, 'jax_aulas', author, text, jax_aulas_routes)
        return jaxaulas_watch(tutorial_id)
    except FileNotFoundError as e:
        return render_template("public/error.html", title="ERROR", error=str(e), year=current_year)

@jax_aulas_routes.route('/jaxaulas/novo', methods=['GET', 'POST'])
def nova_aula():
    from app.uploads.jax_aulas import aulas_novo_id, salvar_json_jaxaulas

    if not current_user.is_authenticated:
        flash('Você precisa estar logado para criar um resumo.', 'warning')
        return redirect(url_for('auth.login'))

    current_user = { "id": current_user.id, "username": current_user.username, "email": current_user.email, "profile": current_user.profile }

    if request.method == 'POST':
        try:
            salvar_json_jaxaulas(request.form, request.files, current_user['username'], aulas_novo_id)
            flash('Aula criada com sucesso!', 'success')
            return render_template('aulas/editar_aula.html', title="Nova Aula", year=current_year, current_user=current_user, aula={})
        except Exception as e:
            flash(f"Ocorreu um erro ao salvar a aula: {e}", 'danger')
            return render_template('aulas/editar_aula.html', title="Nova Aula", year=current_year, current_user=current_user, aula={})

    return render_template('aulas/editar_aula.html', title="Nova Aula", year=current_year, current_user=current_user, aula={})


@jax_aulas_routes.route('/jaxaulas/listar')
def listar_aulas():
    if not current_user.is_authenticated:
        flash('Você precisa estar logado para acessar as aulas.', 'warning')
        return redirect(url_for('auth.login'))

    current_user = { "id": current_user.id, "username": current_user.username, "email": current_user.email, "profile": current_user.profile }
    aulas = []

    from app.uploads.variables import path_app_static_json_jaxaulas as jaxaulas_json_path
    import os, json

    for arquivo in os.listdir(jaxaulas_json_path):
        if arquivo.endswith('.json'):
            with open(os.path.join(jaxaulas_json_path, arquivo), encoding='utf-8') as f:
                try:
                    aulas.append(json.load(f))
                except:
                    continue

    return render_template('aulas/listar_aulas.html', title="Aulas", year=current_year, current_user=current_user, aulas=aulas)

@jax_aulas_routes.route('/jaxaulas/editar/<int:aula_id>', methods=['GET', 'POST'])
def editar_aula(aula_id):
    if not current_user.is_authenticated:
        flash('Você precisa estar logado para editar aulas.', 'warning')
        return redirect(url_for('auth.login'))

    current_user = { "id": current_user.id, "username": current_user.username, "email": current_user.email, "profile": current_user.profile }
    import os, json
    from app.uploads.variables import path_app_static_json_jaxaulas as jaxaulas_json_path

    json_path = os.path.join(jaxaulas_json_path, f"tutorial_{aula_id}.json")

    if not os.path.exists(json_path):
        flash('Aula não encontrada.', 'danger')
        return redirect(url_for('aulas.listar_aulas'))

    with open(json_path, encoding='utf-8') as f:
        aula = json.load(f)

    if request.method == 'POST':
        try:
            aula['title'] = request.form['title']
            aula['subtitle'] = request.form['subtitle']
            aula['theme'] = request.form['theme']
            aula['subtheme'] = request.form['subtheme']
            aula['describe'] = request.form['describe']

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(aula, f, indent=4, ensure_ascii=False)

            flash('Aula atualizada com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao editar a aula: {e}', 'danger')

    return render_template('aulas/editar_aula.html', title="Editar Aula", year=current_year, current_user=current_user, aula=aula)

@jax_aulas_routes.route('/jaxaulas/remover/<int:aula_id>', methods=['POST'])
def remover_aula(aula_id):
    if not current_user.is_authenticated:
        flash('Você precisa estar logado para remover aulas.', 'warning')
        return redirect(url_for('auth.login'))

    current_user = { "id": current_user.id, "username": current_user.username, "email": current_user.email, "profile": current_user.profile }
    import os
    from app.uploads.variables import path_app_static_json_jaxaulas as jaxaulas_json_path

    json_path = os.path.join(jaxaulas_json_path, f"tutorial_{aula_id}.json")

    try:
        if os.path.exists(json_path):
            os.remove(json_path)
            flash('Aula removida com sucesso!', 'success')
        else:
            flash('Aula não encontrada.', 'danger')
    except Exception as e:
        flash(f'Erro ao remover a aula: {e}', 'danger')

    return redirect(url_for('aulas.listar_aulas'))
