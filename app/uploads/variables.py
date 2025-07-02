import os

path_atual = os.path.abspath(__file__)
path_raiz = os.path.dirname(os.path.dirname(os.path.dirname(path_atual)))

path_app = os.path.join(path_raiz, 'app')
path_app_static = os.path.join(path_app, 'static')
path_app_static_images = os.path.join(path_app_static, 'images')
path_app_static_images_jaxaulas = os.path.join(path_app_static_images, 'jax_aulas')
path_app_static_images_jaxaulas_capas = os.path.join(path_app_static_images_jaxaulas, 'capas')
path_app_static_images_jaxaulas_tutotiais = os.path.join(path_app_static_images_jaxaulas, 'tutoriais')
path_app_static_images_jaxresume = os.path.join(path_app_static_images, 'jax_resume')
path_app_static_json = os.path.join(path_app_static, 'json')
path_app_static_json_jaxaulas = os.path.join(path_app_static_json, 'jax_aulas')
path_app_static_json_jaxresume = os.path.join(path_app_static_json, 'jax_resume')

print("Path raiz:", path_raiz)
