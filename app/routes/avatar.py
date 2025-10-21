from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models import get_available_avatar_items, equip_avatar_item, get_user_avatar_data, init_avatar_tables

avatar_routes = Blueprint('avatar', __name__)

@avatar_routes.route('/perfil/avatar')
def avatar_editor():
    """Página de edição do avatar"""
    if 'usuario' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['usuario']['id']
    
    # Inicializar tabelas se necessário
    init_avatar_tables()
    
    # Buscar itens disponíveis por categoria
    hair_items = get_available_avatar_items(user_id, 'hair')
    shirt_items = get_available_avatar_items(user_id, 'shirt')
    pants_items = get_available_avatar_items(user_id, 'pants')
    shoes_items = get_available_avatar_items(user_id, 'shoes')
    accessory_items = get_available_avatar_items(user_id, 'accessory')
    
    current_avatar = get_user_avatar_data(user_id)
    
    return render_template('users/avatar_editor.html',
                         title='Editor de Avatar',
                         hair_items=hair_items,
                         shirt_items=shirt_items,
                         pants_items=pants_items,
                         shoes_items=shoes_items,
                         accessory_items=accessory_items,
                         current_avatar=current_avatar,
                         current_user=session['usuario'])

@avatar_routes.route('/api/avatar/equip', methods=['POST'])
def equip_item():
    """API para equipar item de avatar"""
    if 'usuario' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'})
    
    user_id = session['usuario']['id']
    item_type = request.json.get('item_type')
    item_id = request.json.get('item_id')
    
    if not item_type or not item_id:
        return jsonify({'success': False, 'message': 'Dados inválidos'})
    
    success = equip_avatar_item(user_id, item_type, item_id)
    
    if success:
        # Atualizar avatar na sessão
        session['usuario']['avatar'] = get_user_avatar_data(user_id)
        return jsonify({'success': True, 'message': 'Item equipado com sucesso!'})
    else:
        return jsonify({'success': False, 'message': 'Item não disponível'})

@avatar_routes.route('/api/avatar/current')
def get_current_avatar():
    """API para obter avatar atual"""
    if 'usuario' not in session:
        return jsonify({'success': False})
    
    user_id = session['usuario']['id']
    avatar_data = get_user_avatar_data(user_id)
    
    return jsonify({'success': True, 'avatar': avatar_data})
