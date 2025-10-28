from flask import Blueprint, render_template, redirect, request, flash, url_for, session, json
from flask_login import current_user, login_required
from datetime import datetime, timedelta

def usuario_tem_acesso(perfis_permitidos):
    """
    Verifica se o usuário atual tem acesso baseado nos perfis permitidos
    """
    if not current_user or not current_user.is_authenticated:
        return 'visitante' in perfis_permitidos
    
    perfil_usuario = getattr(current_user, 'profile', 'visitante')
    return perfil_usuario in perfis_permitidos

def obter_perfil_usuario():
    """
    Retorna o perfil do usuário atual
    """
    if current_user and current_user.is_authenticated:
        return getattr(current_user, 'profile', 'visitante')
    return 'visitante'

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



@public_routes.route('/sala-professores/duvidas', methods=['GET', 'POST'])
def sala_professores_duvidas():
    if request.method == 'POST':
        pergunta = request.form.get('pergunta')
        autor = current_user.username if current_user else 'Anônimo'
        
        # Salvar no JSON (similar ao mural)
        duvidas_file = 'app/data/duvidas_academicas.json'
        try:
            with open(duvidas_file, 'r', encoding='utf-8') as f:
                duvidas = json.load(f)
        except:
            duvidas = []
            
        nova_duvida = {
            'id': len(duvidas) + 1,
            'pergunta': pergunta,
            'autor': autor,
            'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'resposta': None,
            'respondido_por': None
        }
        
        duvidas.append(nova_duvida)
        
        with open(duvidas_file, 'w', encoding='utf-8') as f:
            json.dump(duvidas, f, ensure_ascii=False, indent=2)
            
        flash('Dúvida enviada com sucesso!', 'success')
        return redirect(url_for('public.sala_professores_duvidas'))
    
    # Carregar dúvidas existentes
    try:
        with open('app/data/duvidas_academicas.json', 'r', encoding='utf-8') as f:
            duvidas = json.load(f)
    except:
        duvidas = []
        
    return render_template('gamificada/sala_professores.html', 
                         duvidas=duvidas,
                         current_user=current_user,
                         year=current_year)

@public_routes.route('/sala-professores/responder', methods=['POST'])
@login_required
def responder_duvida():
    if current_user.profile not in ['admin', 'funcionario']:
        flash('Apenas funcionários podem responder dúvidas.', 'danger')
        return redirect(url_for('public.sala_professores_duvidas'))
    
    duvida_id = request.form.get('duvida_id')
    resposta = request.form.get('resposta')
    
    try:
        with open('app/data/duvidas_academicas.json', 'r', encoding='utf-8') as f:
            duvidas = json.load(f)
            
        for duvida in duvidas:
            if duvida['id'] == int(duvida_id):
                duvida['resposta'] = resposta
                duvida['respondido_por'] = current_user.username
                break
                
        with open('app/data/duvidas_academicas.json', 'w', encoding='utf-8') as f:
            json.dump(duvidas, f, ensure_ascii=False, indent=2)
            
        flash('Resposta enviada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao responder: {str(e)}', 'danger')
        
    return redirect(url_for('public.sala_professores_duvidas'))

@public_routes.route("/sala-aula/resumos")
def sala_aula_resumos():
    """Página principal de resumos na sala de aula"""
    from app.utils import load_jaxresume
    temas, posts_por_tema, todos_posts = load_jaxresume(public_routes)
    
    # Filtrar posts com base nas permissões
    resumos_acessiveis = []
    for post_id, post in todos_posts.items():
        if usuario_tem_acesso(current_user, post):
            resumos_acessiveis.append(post)
    
    return render_template(
        "resumos/sala_aula.html",
        resumos=resumos_acessiveis,
        temas=temas,
        pode_editar=current_user and current_user.profile in ['admin', 'funcionario'],
        year=current_year,
        current_user=current_user
    )

@public_routes.route("/sala-aula/novo-resumo", methods=['GET', 'POST'])
@login_required
def novo_resumo_sala_aula():
    """Criar novo resumo - apenas admin/funcionários"""
    if current_user.profile not in ['admin', 'funcionario']:
        flash('Apenas administradores e funcionários podem criar resumos.', 'danger')
        return redirect(url_for('resume.sala_aula_resumos'))
    
    from app.uploads.jax_resumos import salvar_json
    
    post = None

    if request.method == 'POST':
        try:
            novo_id = salvar_json(request.form, request.files, current_user.username)
            flash(f'Resumo criado com sucesso! ID: {novo_id}', 'success')
            return redirect(url_for('resume.post', post_id=novo_id))
        except Exception as e:
            flash(f'Ocorreu um erro ao salvar o resumo: {e}', 'danger')

    return render_template('resumos/editar_resumo.html', title="Novo Resumo", year=current_year, current_user=current_user, post=post)

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

@public_routes.route('/educacional')
def educacional():
    # Obter perfil do usuário atual
    perfil_usuario = obter_perfil_usuario()
    
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
        current_user=current_user,
        # PASSANDO AS PERMISSÕES CORRETAMENTE PARA O TEMPLATE - MANTENDO COMPATIBILIDADE
        tem_acesso_mural=usuario_tem_acesso(['aluno', 'admin', 'funcionario']),
        tem_acesso_diretoria=usuario_tem_acesso(['admin', 'funcionario']),
        tem_acesso_professores=usuario_tem_acesso(['admin', 'funcionario'])
    )

@public_routes.route('/entretenimento')
def entretenimento():
    # Para entretenimento, todas as áreas são públicas
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
        current_user=current_user,
        # Todas as áreas de entretenimento são públicas
        tem_acesso_lago=True,
        tem_acesso_esporte=True,
        tem_acesso_cultura=True,
        tem_acesso_nerd=True
    )

@public_routes.route('/empresarial')
def empresarial():
    # Obter perfil do usuário atual
    perfil_usuario = obter_perfil_usuario()
    
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
        current_user=current_user,
        # PASSANDO AS PERMISSÕES CORRETAMENTE
        tem_acesso_tecnica=usuario_tem_acesso(['aluno', 'admin', 'funcionario']),
        tem_acesso_pessoas=usuario_tem_acesso(['admin', 'funcionario']),
        tem_acesso_comercial=usuario_tem_acesso(['aluno', 'admin', 'funcionario']),
        tem_acesso_reunioes=usuario_tem_acesso(['admin', 'funcionario'])
    )
