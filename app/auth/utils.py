import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

PATH_DB = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'data', 'jax.db')
PATH_DB = os.path.normpath(PATH_DB)

def realizar_login(username: str, password: str) -> dict:
    """
    Valida usuário e senha diretamente no banco. Retorna dados do usuário se sucesso.
    """
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, email, password_hash, profile, date_created FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_id, username, email, password_hash_db, profile, date_created = user
        if check_password_hash(password_hash_db, password):
            return {
                "id": user_id,
                "username": username,
                "email": email,
                "profile": profile,
                "date_created": date_created
            }

    return None

def realizar_logout(session_dict: dict) -> None:
    """
    Realiza logout limpando dados da sessão.
    """
    session_dict.clear()

def detalhar_usuario(user_id: int) -> dict:
    """
    Busca os dados completos do usuário com base no ID.
    """
    try:
        user_id = int(user_id)
    except ValueError:
        return None
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, email, profile, date_created FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "profile": user[3],
            "date_created": user[4]
        }

    return None

def criar_conta(username: str, email: str, password: str, profile: str = 'curioso') -> tuple[bool, str]:
    """
    Cria nova conta no banco. Retorna (True, 'mensagem') em caso de sucesso ou (False, 'erro') caso contrário.
    """
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT 1 FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            return False, "Usuário ou e-mail já cadastrados."

        password_hash = generate_password_hash(password)
        date_created = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO users (username, email, password_hash, profile, date_created)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, password_hash, profile, date_created))

        conn.commit()
        return True, "Conta criada com sucesso."

    except sqlite3.Error as e:
        return False, f"Erro ao criar conta: {str(e)}"

    finally:
        conn.close()

def listar_usuarios() -> list[dict]:
    """
    Retorna uma lista de todos os usuários cadastrados no banco.
    """
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, email, profile, date_created FROM users ORDER BY id ASC")
    usuarios = cursor.fetchall()
    conn.close()

    return [
        {
            "id": u[0],
            "username": u[1],
            "email": u[2],
            "profile": u[3],
            "date_created": u[4]
        }
        for u in usuarios
    ]

def atualizar_usuario(user_id: int, username: str = None, email: str = None, password: str = None, profile: str = None) -> tuple[bool, str]:
    """
    Atualiza os dados de um usuário específico. Retorna (True, 'mensagem') em caso de sucesso ou (False, 'erro').
    """
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()

    try:
        # Coleta atual
        cursor.execute("SELECT username, email, profile FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return False, "Usuário não encontrado."

        # Preenche campos que não foram passados
        current_username, current_email, current_profile = user
        username = username or current_username
        email = email or current_email
        profile = profile or current_profile

        # Verifica duplicidade (com exceção do próprio usuário)
        cursor.execute("""
            SELECT 1 FROM users 
            WHERE (username = ? OR email = ?) AND id != ?
        """, (username, email, user_id))
        if cursor.fetchone():
            return False, "Nome de usuário ou e-mail já em uso por outro usuário."

        # Atualiza senha (opcional)
        if password:
            password_hash = generate_password_hash(password)
            cursor.execute("""
                UPDATE users 
                SET username = ?, email = ?, password_hash = ?, profile = ?
                WHERE id = ?
            """, (username, email, password_hash, profile, user_id))
        else:
            cursor.execute("""
                UPDATE users 
                SET username = ?, email = ?, profile = ?
                WHERE id = ?
            """, (username, email, profile, user_id))

        conn.commit()
        return True, "Dados atualizados com sucesso."

    except sqlite3.Error as e:
        return False, f"Erro ao atualizar: {str(e)}"

    finally:
        conn.close()

def remover_usuario(user_id: int) -> tuple[bool, str]:
    """
    Remove um usuário do banco com base no ID. Retorna (True, 'mensagem') ou (False, 'erro').
    """
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT 1 FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            return False, "Usuário não encontrado."

        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True, "Usuário removido com sucesso."

    except sqlite3.Error as e:
        return False, f"Erro ao remover: {str(e)}"

    finally:
        conn.close()
