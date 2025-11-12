"""Serviços de autenticação e gerenciamento de usuários."""
import re
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_DB = os.path.join(BASE_DIR, 'database.db')


class AuthService:
    """Serviço para operações de autenticação."""
    
    @staticmethod
    def realizar_login(username: str, password: str) -> Optional[Dict]:
        """
        Valida usuário e senha. Retorna dados do usuário se sucesso.
        """
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id, username, email, password_hash, profile, date_created FROM users WHERE username = ?", 
                (username,)
            )
            user = cursor.fetchone()
            
            if user and check_password_hash(user[3], password):
                return {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "profile": user[4],
                    "date_created": user[5]
                }
            return None
            
        except Exception as error:
            logger.error("Erro no login: %s", error)
            return None
        finally:
            conn.close()

    @staticmethod
    def criar_conta(username: str, nome_completo: str, email: str, password: str, profile: str = 'curioso') -> Tuple[bool, str]:
        """
        Cria nova conta no banco.
        """
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()

        try:
            # Verifica se usuário ou email já existem
            cursor.execute(
                "SELECT 1 FROM users WHERE username = ? OR email = ?", 
                (username, email)
            )
            if cursor.fetchone():
                return False, "Usuário ou e-mail já cadastrados."

            password_hash = generate_password_hash(password)
            date_created = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO users (username, email, password_hash, profile, date_created, nome_completo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, profile, date_created, nome_completo))

            conn.commit()
            return True, "Conta criada com sucesso."

        except sqlite3.Error as error:
            logger.error("Erro ao criar conta: %s", error)
            return False, f"Erro ao criar conta: {str(error)}"
        finally:
            conn.close()

    @staticmethod
    def detalhar_usuario(user_id: int) -> Optional[Dict]:
        """
        Busca dados completos do usuário.
        """
        try:
            user_id = int(user_id)
        except ValueError:
            return None
            
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id, username, email, profile, date_created, nome_completo FROM users WHERE id = ?", 
                (user_id,)
            )
            user = cursor.fetchone()
            
            if user:
                return {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "profile": user[3],
                    "date_created": user[4],
                    "nome_completo": user[5]
                }
            return None
            
        except Exception as error:
            logger.error("Erro ao buscar usuário: %s", error)
            return None
        finally:
            conn.close()

    @staticmethod
    def listar_usuarios() -> List[Dict]:
        """
        Retorna lista de todos os usuários.
        """
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id, username, email, profile, date_created, nome_completo FROM users ORDER BY id ASC"
            )
            usuarios = cursor.fetchall()
            
            return [
                {
                    "id": u[0],
                    "username": u[1],
                    "email": u[2],
                    "profile": u[3],
                    "date_created": u[4],
                    "nome_completo": u[5]
                }
                for u in usuarios
            ]
        except Exception as error:
            logger.error("Erro ao listar usuários: %s", error)
            return []
        finally:
            conn.close()


class MatriculaService:
    """Serviço para gerenciamento de matrículas."""
    
    @staticmethod
    def listar_matriculas() -> List[Dict]:
        """
        Retorna todas as matrículas cadastradas.
        """
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id, nome_completo, email, status, data_criacao FROM matriculas ORDER BY id DESC"
            )
            registros = cursor.fetchall()
            
            return [
                {
                    "id": r[0],
                    "nome_completo": r[1],
                    "email": r[2],
                    "status": r[3],
                    "data_criacao": r[4]
                }
                for r in registros
            ]
        except Exception as error:
            logger.error("Erro ao listar matrículas: %s", error)
            return []
        finally:
            conn.close()

    @staticmethod
    def validar_matricula(matricula: str, perfil: str) -> bool:
        """
        Valida se a matrícula existe e corresponde ao perfil.
        """
        if not matricula:
            return False
            
        if perfil == "aluno" and not matricula.startswith("275"):
            return False
        if perfil == "funcionario" and not matricula.startswith("255"):
            return False

        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT 1 FROM matriculas WHERE id = ? AND status = 'pendente'", 
                (matricula,)
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def confirmar_matricula(matricula: str) -> bool:
        """
        Atualiza o status da matrícula para 'confirmado'.
        """
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE matriculas SET status = 'confirmado' WHERE id = ?", 
                (matricula,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as error:
            logger.error("Erro ao confirmar matrícula: %s", error)
            return False
        finally:
            conn.close()

    @staticmethod
    def gerar_matricula_personalizada(tipo: str) -> str:
        """
        Gera número de matrícula único baseado no tipo.
        """
        prefixo = "275" if tipo == "aluno" else "255"
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id FROM matriculas WHERE id LIKE ? ORDER BY id DESC LIMIT 1", 
                (f"{prefixo}%",)
            )
            ultimo = cursor.fetchone()
            
            if ultimo:
                match = re.search(r"(\d{3})$", str(ultimo[0]))
                ultimo_num = int(match.group(1)) if match else 0
            else:
                ultimo_num = 0

            novo_num = ultimo_num + 1
            return f"{prefixo}{novo_num:03d}"
        finally:
            conn.close()

    @staticmethod
    def criar_matricula(nome_completo: str, email: str, matricula_id: str) -> Tuple[bool, str]:
        """
        Cria nova matrícula no sistema.
        """
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()
        
        try:
            # Verifica duplicidade
            cursor.execute(
                "SELECT 1 FROM matriculas WHERE email = ? OR id = ?", 
                (email, matricula_id)
            )
            if cursor.fetchone():
                return False, "Já existe uma matrícula com esse e-mail ou número."

            data_criacao = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO matriculas (id, nome_completo, email, status, data_criacao)
                VALUES (?, ?, ?, ?, ?)
            """, (matricula_id, nome_completo, email, 'pendente', data_criacao))
            
            conn.commit()
            return True, "Matrícula criada com sucesso."
            
        except sqlite3.Error as error:
            logger.error("Erro ao criar matrícula: %s", error)
            return False, f"Erro ao criar matrícula: {str(error)}"
        finally:
            conn.close()

    @staticmethod
    def excluir_matricula(matricula_id: str) -> Tuple[bool, Optional[str]]:
        """
        Exclui matrícula do sistema.
        """
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM matriculas WHERE id = ?", (matricula_id,))
            conn.commit()
            return True, None
        except Exception as error:
            logger.error("Erro ao excluir matrícula: %s", error)
            return False, str(error)
        finally:
            conn.close()