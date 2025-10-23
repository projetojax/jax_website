from flask import Blueprint, render_template, redirect, request, flash, url_for, session
from flask_login import current_user
from datetime import datetime, timedelta

public_routes = Blueprint("public", __name__)
current_year = datetime.now().year

@public_routes.before_request
def refresh_session():
    session.permanent = True
    public_routes.permanent_session_lifetime = timedelta(minutes=30)

@public_routes.route("/<path:path>")
def jax_services(path):
    try:
        if '.html' not in path and 'sitemap' not in path:
            return render_template(f'{path}.html', title=path.capitalize(), year=current_year, current_user=current_user)
        elif 'sitemap' in path:
            return render_template('public/sitemap.xml', title='Sitemap', year=current_year, current_user=current_user)
        else:
            return render_template(f'{path}', title=path.capitalize(), year=current_year, current_user=current_user)
    except Exception as e:
        if '.html' in str(e):
            return render_template('public/error.html', title="ERROR", error=f"Página ( {str(e)} ) não encontrada", year=current_year, current_user=current_user)
        return render_template('public/error.html', title="ERROR", error=str(e), year=current_year, current_user=current_user)

@public_routes.route('/')
@public_routes.route('/home')
def home():
    if current_user.is_authenticated:
        return render_template(
            'gamificada/universe.html', 
            title='Home', 
            year=current_year, 
            current_user=current_user, 
            area_name='inicial', 
            area_title='🌍 Universo JAX — Escolha sua Jornada', 
            player_sprite=url_for('static', filename='img/avatar/personagem.png'), 
            default_location='Centro', 
            welcome_message='Explore o Universo JAX e descubra novas oportunidades.', 
            modal_title='🚀 Bem-vindo ao Universo JAX!', 
            modal_message='Explore o futuro da educação, do trabalho e do entretenimento.'
        )

    return render_template('public/home.html', title='Home', year=current_year, current_user=current_user)

@public_routes.route('/google-site-verification=<token>.html')
def google_verification():
    return render_template(
        'public/google-site-verification=OoaVt6jNPKKCO9AiGsIeFX3_muqcrkHbLgRui2LYSRg.html', 
        title='Google Site Verification', 
        year=current_year, 
        current_user=current_user
    )

@public_routes.route('/sitemap')
def sitemap():
    return render_template('public/sitemap.xml', title='Sitemap', year=current_year, current_user=current_user)

@public_routes.route('/sobre')
def sobre():
    return render_template('public/sobre.html', title='Sobre', year=current_year, current_user=current_user)

@public_routes.route('/galeria')
def galeria():
    return render_template('public/galeria.html', title='Galeria', year=current_year, current_user=current_user)

@public_routes.route('/contato')
def contato():
    return render_template('public/contato.html', title='Contato', year=current_year, current_user=current_user)

@public_routes.route('/historia')
def historia():
    return render_template('public/historia.html', title='História', year=current_year, current_user=current_user)

@public_routes.route('/funcionalidades')
def funcionalidades():
    return render_template('public/funcionalidades.html', title='Funcionalidades', year=current_year, current_user=current_user)

@public_routes.route('/documento')
def documento():
    return render_template('public/documento.html', title='Documentacao', year=current_year, current_user=current_user)

@public_routes.route('/jax_jornada')
def jax_jornada():
    return render_template('public/jax_jornada.html', title='Jornada', year=current_year, current_user=current_user)

@public_routes.route('/educacional')
def educacional():
    return render_template(
        'gamificada/universe.html', 
        area_name='educacional', 
        area_title='Campus JAX — Mundo Educacional', 
        player_sprite=url_for('static', filename='img/avatar/personagem.png'), 
        default_location='Pátio', 
        welcome_message='Bem-vindo ao campus.', 
        modal_title='🎓 Bem-vindo!', 
        modal_message='Seja bem-vindo ao Universo Educacional do JAX! Aqui você irá aprender tudo para se capacitar ao mercado e à cidadania contemporânea.', 
        title='Educacional', 
        year=current_year, 
        current_user=current_user
    )

@public_routes.route('/entretenimento')
def entretenimento():
    return render_template(
        'gamificada/universe.html', 
        area_name='entretenimento', 
        area_title='Parque Municipal — Universo Entretenimento JAX', 
        player_sprite=url_for('static', filename='img/avatar/personagem.png'), 
        default_location='Entrada', 
        welcome_message='Bem-vindo ao parque.', 
        modal_title='🎡 Bem-vindo!', 
        modal_message='Seja bem-vindo ao Universo Entretenimento do JAX! Aqui você irá descontrair e lidar com sua saúde mental.', 
        title='Entretenimento', 
        year=current_year, 
        current_user=current_user
    )

@public_routes.route('/empresarial')
def empresarial():
    return render_template(
        'gamificada/universe.html', 
        area_name='empresarial', 
        area_title='🏢 Universo Empresarial JAX', 
        player_sprite=url_for('static', filename='img/avatar/personagem.png'), 
        default_location='Recepção', 
        welcome_message='Bem-vindo ao universo empresarial.', 
        modal_title='🏢 Bem-vindo!', 
        modal_message='Seja bem-vindo ao Universo Empresarial do JAX! Aqui você irá entender como funciona o mercado de trabalho e estar pronto pra lidar com ele.', 
        title='Empresarial', 
        year=current_year, 
        current_user=current_user
    )
