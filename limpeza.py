import os
import shutil

def remove_pycache_dirs(root_dir='.'):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '__pycache__' in dirnames:
            pycache_path = os.path.join(dirpath, '__pycache__')
            print(f'Removendo: {pycache_path}')
            shutil.rmtree(pycache_path)
            dirnames.remove('__pycache__')  # Evita tentar entrar nela

if __name__ == '__main__':
    remove_pycache_dirs('.')