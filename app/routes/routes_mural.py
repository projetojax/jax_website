from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from datetime import datetime
import json, os

mural_pb = Blueprint('mural', __name__)

MURAL_PATH = os.path.join('data', 'mural.json')

def load_mural():
    if os.path.exists(MURAL_PATH):
        with open(MURAL_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_mural(data):
    with open(MURAL_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@mural_pb.route('/mural-oficial', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def mural_oficial():
    mural = load_mural()

    # --- GET: listar ---
    if request.method == 'GET':
        return jsonify(mural)

    # --- Admin-only ---
    if current_user.profile != 'admin':
        return jsonify({'error': 'Acesso negado'}), 403

    # --- POST: adicionar aviso ---
    if request.method == 'POST':
        novo = request.get_json()
        novo['id'] = len(mural) + 1
        novo['data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
        mural.append(novo)
        save_mural(mural)
        return jsonify({'status': 'ok', 'msg': 'Aviso criado com sucesso!'})

    # --- PUT: editar ---
    if request.method == 'PUT':
        dados = request.get_json()
        for aviso in mural:
            if aviso['id'] == dados['id']:
                aviso['titulo'] = dados['titulo']
                aviso['texto'] = dados['texto']
        save_mural(mural)
        return jsonify({'status': 'ok', 'msg': 'Aviso atualizado!'})

    # --- DELETE: apagar ---
    if request.method == 'DELETE':
        dados = request.get_json()
        mural = [m for m in mural if m['id'] != dados['id']]
        save_mural(mural)
        return jsonify({'status': 'ok', 'msg': 'Aviso removido!'})

