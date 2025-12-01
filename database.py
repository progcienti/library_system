import sqlite3
import os
import hashlib
from datetime import datetime, timedelta

DB_FOLDER = "data"
DB_PATH = os.path.join(DB_FOLDER, "library.db")

# multa padrão por dia (em reais)
MULTA_PADRAO_POR_DIA = 0.5

def ensure_db_folder():
    os.makedirs(DB_FOLDER, exist_ok=True)

def get_conn():
    ensure_db_folder()
    return sqlite3.connect(DB_PATH)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def criar_tabelas():
    """
    Cria tabelas (ou atualiza o esquema se necessário).
    Essa função é segura para rodar várias vezes.
    """
    ensure_db_folder()
    conn = get_conn()
    c = conn.cursor()

    # usuarios
    c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT,
        login TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL DEFAULT 'user',
        criado_em TEXT NOT NULL
    )
    ''')

    # livros (adicionando coluna tipo)
    c.execute('''
    CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT,
        ano INTEGER,
        isbn TEXT,
        qtd INTEGER NOT NULL DEFAULT 1,
        tipo TEXT DEFAULT 'Geral'
    )
    ''')

    # emprestimos (adicionando campo multa e data_devolucao)
    c.execute('''
    CREATE TABLE IF NOT EXISTS emprestimos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        livro_id INTEGER NOT NULL,
        data_emprestimo TEXT NOT NULL,
        prazo_devolucao TEXT NOT NULL,
        devolvido INTEGER NOT NULL DEFAULT 0,
        data_devolucao TEXT,
        multa REAL DEFAULT 0,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(livro_id) REFERENCES livros(id)
    )
    ''')
    conn.commit()
    conn.close()

    criar_admin_padrao()
    migrar_schema_se_necessario()

def criar_admin_padrao():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM usuarios WHERE login = ?", ("admin",))
    if not c.fetchone():
        agora = datetime.utcnow().isoformat()
        senha_hash = hash_password("1234")
        c.execute("INSERT INTO usuarios (nome, email, login, senha, tipo, criado_em) VALUES (?,?,?,?,?,?)",
                  ("Administrador", "admin@local", "admin", senha_hash, "admin", agora))
        conn.commit()
    conn.close()

def migrar_schema_se_necessario():
    """
    Adiciona colunas se o DB antigo não tiver.
    """
    conn = get_conn()
    c = conn.cursor()
    # verificar coluna 'tipo' em livros
    try:
        c.execute("PRAGMA table_info(livros)")
        cols = [r[1] for r in c.fetchall()]
        if 'tipo' not in cols:
            c.execute("ALTER TABLE livros ADD COLUMN tipo TEXT DEFAULT 'Geral'")
    except Exception:
        pass

    # verificar coluna 'multa' em emprestimos
    try:
        c.execute("PRAGMA table_info(emprestimos)")
        cols2 = [r[1] for r in c.fetchall()]
        if 'multa' not in cols2:
            c.execute("ALTER TABLE emprestimos ADD COLUMN multa REAL DEFAULT 0")
    except Exception:
        pass

    conn.commit()
    conn.close()

# Configuração da multa
def get_multa_por_dia():
    return MULTA_PADRAO_POR_DIA

def set_multa_por_dia(valor):
    global MULTA_PADRAO_POR_DIA
    MULTA_PADRAO_POR_DIA = float(valor)

# ------------------ Usuários ------------------
def inserir_usuario(nome, email, login, senha, tipo="user"):
    conn = get_conn()
    c = conn.cursor()
    try:
        senha_hash = hash_password(senha)
        criado_em = datetime.utcnow().isoformat()
        c.execute("INSERT INTO usuarios (nome,email,login,senha,tipo,criado_em) VALUES (?,?,?,?,?,?)",
                  (nome, email, login, senha_hash, tipo, criado_em))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()

def verificar_login(login, senha):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, nome, login, senha, tipo FROM usuarios WHERE login = ?", (login,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    stored_hash = row[3]
    if hash_password(senha) == stored_hash:
        return (row[0], row[1], row[2], row[4])  # id, nome, login, tipo
    return None

def listar_usuarios():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, nome, email, login, tipo, criado_em FROM usuarios ORDER BY nome")
    rows = c.fetchall()
    conn.close()
    return rows

# ------------------ Livros ------------------
def inserir_livro(titulo, autor, ano, isbn, qtd, tipo="Geral"):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO livros (titulo,autor,ano,isbn,qtd,tipo) VALUES (?,?,?,?,?,?)",
              (titulo, autor, ano, isbn, qtd, tipo))
    conn.commit()
    conn.close()

def listar_livros():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, titulo, autor, ano, isbn, qtd, tipo FROM livros ORDER BY titulo")
    rows = c.fetchall()
    conn.close()
    return rows

def buscar_livro_por_id(livro_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, titulo, autor, ano, isbn, qtd, tipo FROM livros WHERE id = ?", (livro_id,))
    row = c.fetchone()
    conn.close()
    return row

def atualizar_livro(livro_id, titulo, autor, ano, isbn, qtd, tipo):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE livros SET titulo=?, autor=?, ano=?, isbn=?, qtd=?, tipo=? WHERE id=?
    """, (titulo, autor, ano, isbn, qtd, tipo, livro_id))
    conn.commit()
    conn.close()

def atualizar_quantidade(livro_id, nova_qtd):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE livros SET qtd = ? WHERE id = ?", (nova_qtd, livro_id))
    conn.commit()
    conn.close()

def remover_livro(livro_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
    conn.commit()
    conn.close()

# ------------------ Empréstimos ------------------
def emprestar_livro(usuario_id, livro_id, dias_prazo=14):
    conn = get_conn()
    c = conn.cursor()
    livro = buscar_livro_por_id(livro_id)
    if not livro:
        conn.close()
        return False, "Livro não encontrado"
    if livro[5] <= 0:
        conn.close()
        return False, "Livro indisponível (quantidade = 0)"

    data_e = datetime.utcnow()
    prazo = data_e + timedelta(days=dias_prazo)
    c.execute(
        "INSERT INTO emprestimos (usuario_id, livro_id, data_emprestimo, prazo_devolucao, devolvido, multa) VALUES (?,?,?,?,0,0)",
        (usuario_id, livro_id, data_e.isoformat(), prazo.isoformat())
    )
    c.execute("UPDATE livros SET qtd = qtd - 1 WHERE id = ?", (livro_id,))
    conn.commit()
    conn.close()
    return True, None

def listar_emprestimos_usuario(usuario_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        SELECT e.id, l.titulo, l.tipo, e.data_emprestimo, e.prazo_devolucao, e.devolvido, e.data_devolucao, e.multa, l.isbn
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        WHERE e.usuario_id = ?
        ORDER BY e.data_emprestimo DESC
    ''', (usuario_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def listar_emprestimos_ativos():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        SELECT e.id, u.nome, l.titulo, l.tipo, e.data_emprestimo, e.prazo_devolucao, e.devolvido, e.data_devolucao, e.multa
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        JOIN usuarios u ON e.usuario_id = u.id
        ORDER BY e.data_emprestimo DESC
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def devolver_livro(emprestimo_id, multa_calculada=0):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT livro_id, devolvido FROM emprestimos WHERE id = ?", (emprestimo_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "Empréstimo não encontrado"
    livro_id, devolvido = row
    if devolvido:
        conn.close()
        return False, "Já devolvido"
    data_dev = datetime.utcnow().isoformat()
    c.execute("UPDATE emprestimos SET devolvido = 1, data_devolucao = ?, multa = ? WHERE id = ?", (data_dev, multa_calculada, emprestimo_id))
    c.execute("UPDATE livros SET qtd = qtd + 1 WHERE id = ?", (livro_id,))
    conn.commit()
    conn.close()
    return True, None

# Relatórios simples / contadores para dashboard
def contar_total_livros():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM livros")
    v = c.fetchone()[0]
    conn.close()
    return v

def contar_total_usuarios():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM usuarios")
    v = c.fetchone()[0]
    conn.close()
    return v

def contar_emprestimos_ativos():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM emprestimos WHERE devolvido = 0")
    v = c.fetchone()[0]
    conn.close()
    return v

def contar_atrasados():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT prazo_devolucao FROM emprestimos WHERE devolvido = 0")
    rows = c.fetchall()
    atrasos = 0
    now = datetime.utcnow()
    for (p,) in rows:
        try:
            prazo = datetime.fromisoformat(p)
            if now.date() > prazo.date():
                atrasos += 1
        except Exception:
            pass
    conn.close()
    return atrasos

# Estatísticas de multas
def total_multas_geradas():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT SUM(multa) FROM emprestimos")
    v = c.fetchone()[0] or 0
    conn.close()
    return v

# Relatório mais emprestados (pandas)
def relatorio_mais_emprestados(limit=10):
    import pandas as pd
    conn = get_conn()
    df = pd.read_sql_query('''
        SELECT l.titulo, COUNT(e.id) AS total
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        GROUP BY l.titulo
        ORDER BY total DESC
        LIMIT ?
    ''', conn, params=(limit,))
    conn.close()
    return df
