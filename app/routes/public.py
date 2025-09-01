from flask import Blueprint, render_template, Flask, redirect, request, session, flash, url_for
from datetime import datetime

public_routes = Blueprint("public", __name__)
current_year = datetime.now().year

from flask import session
from datetime import timedelta

@public_routes.before_request
def refresh_session():
    session.permanent = True
    public_routes.permanent_session_lifetime = timedelta(minutes=30)

@public_routes.route("/<path:path>")
def jax_services(path):
    try:
        if '.html' not in path and 'sitemap' not in path:
            return render_template(f'{path}.html', title=path.capitalize(), year=current_year)
        elif 'sitemap' in path:
            return render_template('sitemap.xml', title='Sitemap', year=current_year)
        else:
            return render_template(f'{path}', title=path.capitalize(), year=current_year)
    except Exception as e:
        if '.html' in str(e):
            return render_template('error.html', title="ERROR", error=f"Página ( {str(e)} ) não encontrada")
        return render_template('error.html', title="ERROR", error=str(e))

@public_routes.route('/')
@public_routes.route('/home')
def home():

    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('home.html', title='Home', year=current_year, current_user=usuario)

    return render_template('home.html', title='Home', year=current_year)

@public_routes.route('/google-site-verification=<token>.html')
def google_verification():
    return render_template('google-site-verification=OoaVt6jNPKKCO9AiGsIeFX3_muqcrkHbLgRui2LYSRg.html', title='Google Site Verification', year=current_year)

@public_routes.route('/sitemap')
def sitemap():
    return render_template('sitemap.xml', title='Sitemap', year=current_year)

@public_routes.route('/sobre')
def sobre():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('sobre.html', title='Sobre', year=current_year, current_user=usuario)
    return render_template('sobre.html', title='Sobre', year=current_year)

@public_routes.route('/galeria')
def galeria():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('galeria.html', title='Galeria', year=current_year, current_user=usuario)
    return render_template('galeria.html', title='Galeria', year=current_year)

@public_routes.route('/contato')
def contato():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('contato.html', title='Contato', year=current_year, current_user=usuario)
    return render_template('contato.html', title='Contato', year=current_year)

@public_routes.route('/historia')
def historia():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('historia.html', title='História', year=current_year, current_user=usuario)
    return render_template('historia.html', title='História', year=current_year)

@public_routes.route('/funcionalidades')
def funcionalidades():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('funcionalidades.html', title='Funcionalidades', year=current_year, current_user=usuario)
    return render_template('funcionalidades.html', title='Funcionalidades', year=current_year)

@public_routes.route('/documento')
def documento():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('documento.html', title='Documentacao', year=current_year, current_user=usuario) 
    return render_template('documento.html', title='Documentacao', year=current_year)

@public_routes.route('/jax_jornada')
def jax_jornada():
    if 'usuario' in session:
        usuario = session['usuario']
        return render_template('jax_jornada.html', title='Jornada', year=current_year, current_user=usuario)
    return render_template('jax_jornada.html', title='Jornada', year=current_year)
