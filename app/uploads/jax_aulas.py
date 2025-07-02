from .variables import path_app_static_images_jaxaulas_capas as jaxaulas_capas_path
from .variables import path_app_static_images_jaxaulas_tutotiais as jaxaulas_tutoriais_path
from .variables import path_app_static_json_jaxaulas as jaxaulas_json_path
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

def aulas_novo_id(prefixo: str):
    """
    Gera um novo ID baseado nos arquivos JSON existentes no diretório de jaxaulas.
    Retorna o maior ID encontrado + 1.
    """
    # Lista os arquivos na pasta de JSON
    arquivos_json = [f for f in os.listdir(jaxaulas_json_path) if f.endswith('.json')]

    # Caso não existam arquivos, o primeiro ID será 1
    if not arquivos_json:
        return 1

    # Extrai o ID de cada arquivo JSON
    ids = []
    for arquivo in arquivos_json:
        try:
            # Abre o arquivo e carrega o JSON
            with open(os.path.join(jaxaulas_json_path, arquivo), 'r', encoding='utf-8') as f:
                dados = json.load(f)
                # Assumindo que o ID está na chave 'id'
                ids.append(dados['id'])
        except Exception as e:
            print(f"Erro ao processar o arquivo {arquivo}: {e}")

    # Retorna o maior ID encontrado + 1
    return max(ids) + 1 if ids else 1

def salvar_json_jaxaulas(form, files, autor, aulas_novo_id_func):
    # Gera ID único
    novo_id = aulas_novo_id_func('jaxaulas')

    # Trata arquivos
    imagem = files['capa']
    video = files['video']

    nome_imagem = secure_filename(imagem.filename)
    nome_video = secure_filename(video.filename)

    imagem.save(os.path.join(jaxaulas_capas_path, nome_imagem))
    video.save(os.path.join(jaxaulas_tutoriais_path, nome_video))

    # Monta dicionário JSON
    data = {
        "id": novo_id,
        "title": form['title'],
        "subtitle": form['subtitle'],
        "author": autor,
        "theme": form['theme'],
        "subtheme": form['subtheme'],
        "date_published": datetime.now().strftime("%Y-%m-%d"),
        "capa": nome_imagem,
        "video": nome_video,
        "describe": form['describe'],
        "comments": []
    }

    # Salva JSON em arquivo
    json_path = os.path.join(jaxaulas_json_path, f"tutorial_{novo_id}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return novo_id
