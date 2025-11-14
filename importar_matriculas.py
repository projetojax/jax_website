import pandas as pd
import sqlite3
from datetime import datetime
import os

# Caminho correto para o banco REAL usado pelo site
PATH_DB = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'app',
    'static',
    'data',
    'jax.db'
)

def importar_matriculas():
    CSV_FILE = 'backup_matriculas.csv'

    # Verificações
    if not os.path.exists(PATH_DB):
        print("❌ Banco de dados não encontrado em:", PATH_DB)
        return

    if not os.path.exists(CSV_FILE):
        print("❌ CSV não encontrado:", CSV_FILE)
        return

    # Conectar ao banco real
    conn = sqlite3.connect(PATH_DB)
    cursor = conn.cursor()

    try:
        df = pd.read_csv(CSV_FILE)
        print(f"Encontradas {len(df)} matrículas no backup")

        for index, row in df.iterrows():

            numero_matricula = row['Nº Matrícula']
            nome_completo = row['Nome']
            email = row['Email']
            status = row['Status']
            data_csv = row['Data']

            # converter a data
            try:
                data_criacao = datetime.fromisoformat(data_csv)
            except:
                try:
                    data_criacao = datetime.strptime(data_csv, "%d/%m/%Y %H:%M:%S")
                except:
                    data_criacao = datetime.utcnow()

            print(f"Processando: {nome_completo} (Matrícula: {numero_matricula})")

            # Verificar se já existe
            cursor.execute(
                "SELECT id FROM matriculas WHERE id = ? OR email = ?",
                (numero_matricula, email)
            )
            existing = cursor.fetchone()

            if existing:
                print(f"⚠️ Matrícula {numero_matricula} já existe. Atualizando...")

                cursor.execute("""
                    UPDATE matriculas SET
                        nome_completo = ?,
                        email = ?,
                        status = ?,
                        data_criacao = ?
                    WHERE id = ?
                """, (nome_completo, email, status, data_criacao, numero_matricula))

            else:
                print(f"➕ Adicionando nova matrícula: {numero_matricula}")

                cursor.execute("""
                    INSERT INTO matriculas
                        (id, nome_completo, email, status, data_criacao)
                    VALUES (?, ?, ?, ?, ?)
                """, (numero_matricula, nome_completo, email, status, data_criacao))

        conn.commit()
        print("✅ Importação de matrículas concluída com sucesso!")

    except Exception as e:
        print("❌ Erro durante a importação:", e)
        conn.rollback()

    finally:
        conn.close()


if __name__ == "__main__":
    importar_matriculas()
