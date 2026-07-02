import sqlite3

DB_NAME = "usuarios.db"

def inicializar_banco():
    """Cria o arquivo de banco de dados e as tabelas se não existirem."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                cpf TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                genero TEXT NOT NULL
            )
        """)
        
        # Tabela para armazenar a memória da IA (chat_id alterado para TEXT para o Instagram)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_conversas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Lista de teste
        usuarios_teste = [
            ("12345678900", "Amanda Souza", "F"),
            ("98765432100", "Carlos Silva", "M"),
            ("11122233344", "Fernanda Ribeiro", "F"),
            ("55566677788", "João Pereira", "M"),
            ("99988877766", "Mariana Costa", "F")
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO usuarios (cpf, nome, genero) 
            VALUES (?, ?, ?)
        """, usuarios_teste)
        
        conn.commit()

def consultar_cadastro(cpf):
    """Busca o farmacêutico pelo CPF e retorna um dicionário ou None."""
    cpf_limpo = "".join(filter(str.isdigit, str(cpf)))
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome, genero FROM usuarios WHERE cpf = ?", (cpf_limpo,))
        resultado = cursor.fetchone()
        
    if resultado:
        return {"nome": resultado[0], "genero": resultado[1]}
    return None

# ==========================================================
# FUNÇÕES PARA A MEMÓRIA DA IA (ADAPTADAS PARA INSTAGRAM)
# ==========================================================

def salvar_mensagem_historico(chat_id, role, content):
    """Salva uma mensagem (do usuário ou da IA) no banco de dados. Aceita chat_id como string."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO historico_conversas (chat_id, role, content)
            VALUES (?, ?, ?)
        """, (str(chat_id), role, content))
        conn.commit()

def buscar_historico(chat_id, limite=20):
    """Busca as últimas mensagens do chat para servir de contexto."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content FROM (
                SELECT role, content, id FROM historico_conversas 
                WHERE chat_id = ? 
                ORDER BY id DESC LIMIT ?
            ) ORDER BY id ASC
        """, (str(chat_id), limite))
        
        resultados = cursor.fetchall()
        
    return [{"role": r[0], "content": r[1]} for r in resultados]

def limpar_historico(chat_id):
    """Apaga a memória do chat quando o usuário sai do modo IA."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM historico_conversas WHERE chat_id = ?", (str(chat_id),))
        conn.commit()

def armazenar_conversa(chat_id, mensagens):
    """Armazena uma lista de mensagens no banco de dados."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        for msg in mensagens:
            cursor.execute("""
                INSERT INTO historico_conversas (chat_id, role, content)
                VALUES (?, ?, ?)
            """, (str(chat_id), msg['role'], msg['content']))
        conn.commit()