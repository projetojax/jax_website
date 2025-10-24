from flask import Blueprint, render_template, redirect, request, flash, url_for, jsonify
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from app.utils import usuario_tem_acesso

resume_routes = Blueprint("resume", __name__)
current_year = datetime.now().year

@resume_routes.route("/jaxresume")
def jaxresume():
    from app.utils import load_jaxresume
    temas, _, _ = load_jaxresume(resume_routes)

    return render_template(
        "resumos/jaxresume.html",
        temas=temas,
        year=current_year,
        current_user=current_user
    )

@resume_routes.route("/jaxresume/<tema>")
def temas(tema):
    from app.utils import load_jaxresume
    tema = str(tema).capitalize()
    all_posts = load_jaxresume(resume_routes)[1].get(tema)

    if all_posts is None:
        return render_template("public/error.html", title="ERROR", error="Tema não encontrado", year=current_year)

    # marcar posts com flag de acesso
    posts = []
    for post in all_posts:
        resumo = load_jaxresume(resume_routes)[2].get(post['id'])
        tem_acesso = usuario_tem_acesso(current_user, resumo) if resumo else False
        posts.append({**post, "sem_acesso": not tem_acesso})

    return render_template("resumos/lista_posts.html", posts=posts, tema=tema, year=current_year, current_user=current_user)

@resume_routes.route("/jaxresume/post/<int:post_id>")
def post(post_id):
    from app.utils import load_jaxresume

    resumo = load_jaxresume(resume_routes)[2].get(post_id)
    if resumo is None:
        return render_template("public/error.html", title="ERROR", error="Post não encontrado", year=current_year)

    if not usuario_tem_acesso(current_user, resumo):
        return render_template("error.html", title="ERROR", error="Você não tem permissão para acessar este resumo.", year=current_year)

    return render_template("resumos/post_completo.html", post=resumo, year=current_year, current_user=current_user)

@resume_routes.route("/jaxresume/post/<post_id>/add_comment", methods=["POST"])
def add_comment_jaxresume(post_id):
    from app.utils import add_comment
    
    # Se o usuário estiver logado, usa o nome dele, senão "anônimo"
    author = current_user.username if current_user.is_authenticated else "anônimo"
    text = request.form.get("text")

    if not text:
        flash("Comentário não pode estar vazio.", "danger")
        return post(post_id)

    try:
        add_comment(post_id, 'jax_resume', author, text, resume_routes)
        flash("Comentário adicionado com sucesso!", "success")
        return redirect(url_for('resume.post', post_id=post_id))
    except FileNotFoundError as e:
        return render_template("public/error.html", title="ERROR", error=str(e), year=current_year)

@resume_routes.route('/jaxresume/novo', methods=['GET', 'POST'])
@login_required
def novo_resumo():
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

@resume_routes.route('/jaxresume/lista')
@login_required
def lista_resumos():
    from app.uploads.jax_resumos import listar_resumos
    
    resumos = listar_resumos()
    return render_template('resumos/lista_resumos.html', resumos=resumos, year=current_year, current_user=current_user)

@resume_routes.route('/jaxresume/editar/<int:post_id>', methods=['GET', 'POST'])
@login_required
def editar_resumo(post_id):
    from app.utils import load_jaxresume
    from app.uploads.jax_resumos import salvar_json

    post_data = load_jaxresume(resume_routes)[2].get(post_id)
    
    if not post_data:
        flash('Resumo não encontrado.', 'danger')
        return redirect(url_for('resume.lista_resumos'))

    if request.method == 'POST':
        try:
            salvar_json(request.form, request.files, current_user.username, post_id=post_id)
            flash('Resumo atualizado com sucesso!', 'success')
            return redirect(url_for('resume.post', post_id=post_id))
        except Exception as e:
            flash(f'Ocorreu um erro ao atualizar: {e}', 'danger')

    return render_template('resumos/editar_resumo.html', title="Editar Resumo", year=current_year, current_user=current_user, post=post_data)

@resume_routes.route('/jaxresume/remover/<int:id>', methods=['POST'])
@login_required
def remover_resumo(id):
    from app.uploads.jax_resumos import remover_resumo_por_id, listar_resumos
    
    try:
        remover_resumo_por_id(id)
        flash("Resumo removido com sucesso.", "success")
    except Exception as e:
        flash(f"Erro ao remover resumo: {e}", "danger")

    resumos = listar_resumos()
    return render_template('resumos/lista_resumos.html', resumos=resumos, year=current_year, current_user=current_user)

@resume_routes.route("/api/jaxresume/resumos")
def api_lista_resumos():
    """API: Lista todos os resumos com filtro de acesso - VERSÃO CORRIGIDA"""
    try:
        from app.utils import load_jaxresume, usuario_tem_acesso
        
        # Carrega os dados dos resumos
        _, _, todos_posts = load_jaxresume(resume_routes)
        
        print(f"DEBUG: Total de posts carregados: {len(todos_posts)}")
        
        # Se não há posts, retorna array vazio
        if not todos_posts:
            return jsonify({
                'success': True,
                'count': 0,
                'resumos': [],
                'user_info': {
                    'is_authenticated': current_user and current_user.is_authenticated,
                    'profile': getattr(current_user, 'profile', 'visitante') if current_user and current_user.is_authenticated else 'visitante',
                    'can_edit': current_user and current_user.is_authenticated and getattr(current_user, 'profile', '') in ['admin', 'funcionario']
                }
            })
        
        # Filtrar resumos baseado nas permissões do usuário
        resumos_acessiveis = []
        
        for post_id, post in todos_posts.items():
            try:
                # Verifica se o usuário tem acesso ao post
                tem_acesso = usuario_tem_acesso(current_user, post)
                
                if tem_acesso:
                    # CORREÇÃO: Usa os campos em inglês que vêm da função load_jaxresume
                    resumo_simplificado = {
                        'id': post_id,
                        'titulo': post.get('title', 'Sem título'),  # title em inglês
                        'descricao': post.get('subtitle', 'Sem descrição'),  # subtitle em inglês
                        'tema': post.get('theme', 'Geral'),  # theme em inglês
                        'autor': post.get('author', 'Anônimo'),  # author em inglês
                        'data_publicacao': post.get('date_published', ''),  # date_published em inglês
                        'imagem_url': post.get('image', ''),  # image em inglês
                        'acesso_liberado': True,
                        'pode_editar': current_user and current_user.is_authenticated and getattr(current_user, 'profile', '') in ['admin', 'funcionario']
                    }
                    resumos_acessiveis.append(resumo_simplificado)
                    print(f"DEBUG: Resumo {post_id} - Título: {resumo_simplificado['titulo']}")
                    
            except Exception as e:
                print(f"DEBUG: Erro ao processar post {post_id}: {str(e)}")
                continue
        
        print(f"DEBUG: Resumos acessíveis encontrados: {len(resumos_acessiveis)}")
        
        # Prepara informações do usuário
        user_info = {
            'is_authenticated': current_user and current_user.is_authenticated,
            'profile': getattr(current_user, 'profile', 'visitante') if current_user and current_user.is_authenticated else 'visitante',
            'can_edit': current_user and current_user.is_authenticated and getattr(current_user, 'profile', '') in ['admin', 'funcionario']
        }
        
        response_data = {
            'success': True,
            'count': len(resumos_acessiveis),
            'resumos': resumos_acessiveis,
            'user_info': user_info
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"DEBUG: Erro crítico na API: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Retorna erro em formato JSON
        return jsonify({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}',
            'resumos': [],
            'user_info': {
                'is_authenticated': False,
                'profile': 'visitante',
                'can_edit': False
            }
        }), 500

@resume_routes.route("/api/jaxresume/resumo/<int:post_id>")
def api_resumo_detalhe(post_id):
    """API: Detalhes completos de um resumo específico"""
    from app.utils import load_jaxresume
    
    try:
        resumo = load_jaxresume(resume_routes)[2].get(post_id)
        
        if resumo is None:
            return jsonify({
                'success': False,
                'error': 'Resumo não encontrado'
            }), 404

        if not usuario_tem_acesso(current_user, resumo):
            return jsonify({
                'success': False,
                'error': 'Acesso não autorizado a este resumo'
            }), 403

        # Retorna o resumo completo
        return jsonify({
            'success': True,
            'resumo': resumo
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@resume_routes.route("/api/jaxresume/temas")
def api_lista_temas():
    """API: Lista todos os temas disponíveis"""
    from app.utils import load_jaxresume
    
    try:
        temas, posts_por_tema, _ = load_jaxresume(resume_routes)
        
        temas_com_contagem = []
        for tema in temas:
            posts_do_tema = posts_por_tema.get(tema, [])
            # Filtrar apenas posts com acesso
            posts_acessiveis = [p for p in posts_do_tema if usuario_tem_acesso(current_user, p)]
            
            temas_com_contagem.append({
                'nome': tema,
                'quantidade_resumos': len(posts_acessiveis),
                'acessivel': len(posts_acessiveis) > 0
            })
        
        return jsonify({
            'success': True,
            'temas': temas_com_contagem
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@resume_routes.route("/api/jaxresume/tema/<string:tema_nome>")
def api_resumos_por_tema(tema_nome):
    """API: Lista resumos por tema específico"""
    from app.utils import load_jaxresume
    
    try:
        tema_nome = tema_nome.capitalize()
        _, posts_por_tema, _ = load_jaxresume(resume_routes)
        
        posts_do_tema = posts_por_tema.get(tema_nome, [])
        
        # Filtrar posts com acesso
        resumos_acessiveis = []
        for post in posts_do_tema:
            resumo_completo = load_jaxresume(resume_routes)[2].get(post['id'])
            if resumo_completo and usuario_tem_acesso(current_user, resumo_completo):
                resumo_simplificado = {
                    'id': post['id'],
                    'titulo': post.get('titulo', 'Sem título'),
                    'descricao': post.get('descricao', 'Sem descrição'),
                    'autor': post.get('autor', 'Anônimo'),
                    'data_publicacao': post.get('data_publicacao', '')
                }
                resumos_acessiveis.append(resumo_simplificado)
        
        return jsonify({
            'success': True,
            'tema': tema_nome,
            'count': len(resumos_acessiveis),
            'resumos': resumos_acessiveis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@resume_routes.route("/sala-aula/resumos-data")
def sala_aula_resumos_data():
    """Rota específica para a sala de aula gamificada"""
    return api_lista_resumos()


