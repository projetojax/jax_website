from .variables import path_app_static_images_jaxresume as jaxresume_path
from .variables import path_app_static_json_jaxresume as jaxresume_json_path
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime

def resumo_novo_id(prefixo: str):
    """
    Gera um novo ID baseado nos arquivos JSON existentes no diretório de jaxaulas.
    Retorna o maior ID encontrado + 1.
    """
    # Lista os arquivos na pasta de JSON
    arquivos_json = [f for f in os.listdir(jaxresume_json_path) if f.endswith('.json')]

    # Caso não existam arquivos, o primeiro ID será 1
    if not arquivos_json:
        return 1

    # Extrai o ID de cada arquivo JSON
    ids = []
    for arquivo in arquivos_json:
        try:
            # Abre o arquivo e carrega o JSON
            with open(os.path.join(jaxresume_json_path, arquivo), 'r', encoding='utf-8') as f:
                dados = json.load(f)
                # Assumindo que o ID está na chave 'id'
                ids.append(dados['id'])
        except Exception as e:
            print(f"Erro ao processar o arquivo {arquivo}: {e}")

    # Retorna o maior ID encontrado + 1
    return max(ids) + 1 if ids else 1

def salvar_json(form_data, files, autor):
    # Gera o ID único para o novo resumo
    novo_id = resumo_novo_id('jaxresume')

    # Salva a imagem de capa
    capa = files['image']
    nome_imagem = secure_filename(capa.filename)  # Garante que o nome seja seguro
    capa.save(os.path.join(jaxresume_path, nome_imagem))  # Salva a imagem no diretório

    # Cria os dados que serão salvos no JSON
    data = {
        "id": novo_id,
        "title": form_data['title'],
        "subtitle": form_data.get('subtitle', ''),  # Subtítulo pode ser vazio
        "author": autor,
        "theme": form_data.get('theme', ''),
        "subtheme": form_data.get('subtheme', ''),
        "date_published": form_data.get('date_published', datetime.now().strftime("%Y-%m-%d")),
        "image": nome_imagem,  # O nome da imagem salva
        "content": form_data['content'],
        "comments": []  # Comentários podem ser uma lista vazia inicialmente
    }

    # Salva o JSON no diretório específico
    json_path = os.path.join(jaxresume_json_path, f"post_{novo_id}.json")
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    return novo_id
