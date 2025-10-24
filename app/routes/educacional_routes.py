from flask import Blueprint, render_template, jsonify, request
from flask_login import current_user, login_required
from datetime import datetime

educacional_routes = Blueprint('educacional_routes', __name__)

# Mural Oficial (avisos da escola)
@educacional_routes.route('/mural-oficial')
@login_required
def mural_oficial():
    # Aqui futuramente você pode puxar do banco
    avisos = [
        {"titulo": "Semana de Integração", "texto": "Participe da semana JAX de boas-vindas!", "data": "2025-10-24"},
        {"titulo": "Prazo de Inscrição", "texto": "Último dia para se inscrever no curso de Cidadania Digital.", "data": "2025-10-30"},
    ]
    return jsonify(avisos)


# Sala da Diretoria (chat com admins)
chat_mensagens = []

@educacional_routes.route('/diretoria-chat', methods=['GET', 'POST'])
@login_required
def diretoria_chat():
    if request.method == 'POST':
        msg = request.json.get('mensagem')
        if msg:
            chat_mensagens.append({
                "usuario": current_user.username,
                "perfil": current_user.profile,
                "mensagem": msg,
                "data": datetime.now().strftime("%H:%M:%S")
            })
        return jsonify(success=True)

    return jsonify(chat_mensagens)
