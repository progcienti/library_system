import sqlite3
from datetime import datetime, timedelta

# --------------------------
# Funções de Conexão e Setup
# --------------------------

def conectar():
    return sqlite3.connect("data/library.db")

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    # --- Tabela de usuários ---
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT,
        login TEXT UNIQUE,
        senha TEXT
    )''')

    # Corrige tabelas antigas — adiciona coluna "tipo" se não existir
    c.execute("PRAGMA table_info(usuarios)")
    colunas = [col[1] for col in c.fetchall()]
    if "tipo" not in colunas:
        try:
            c.execute("ALTER TABLE usuarios ADD COLUMN tipo TEXT DEFAULT 'usuario'")
            print("✅ Coluna 'tipo' adicionada automaticamente em 'usuarios'")
        except:
            pass

    # --- Tabela de livros ---
    c.execute('''CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        autor TEXT,
        ano INTEGER,
        isbn TEXT,
        quantidade INTEGER
    )''')

    # --- Tabela de empréstimos ---
    c.execute('''CREATE TABLE IF NOT EXISTS emprestimos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        livro_id INTEGER,
        data_emprestimo TEXT,
        prazo_devolucao TEXT,
        devolvido INTEGER DEFAULT 0,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(livro_id) REFERENCES livros(id)
    )''')

    # --- Garante a existência do admin ---
    c.execute("SELECT * FROM usuarios WHERE login='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO usuarios (nome, email, login, senha, tipo) VALUES (?, ?, ?, ?, ?)",
                  ("Bibliotecário", "admin@library.com", "admin", "1234", "admin"))

    conn.commit()
    conn.close()



# --------------------------
# Funções de Usuários
# --------------------------

def inserir_usuario(nome, email, login, senha):
    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT INTO usuarios (nome, email, login, senha) VALUES (?, ?, ?, ?)",
              (nome, email, login, senha))
    conn.commit()
    conn.close()

def verificar_login(login, senha):
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE login=? AND senha=?", (login, senha))
    user = c.fetchone()
    conn.close()
    return user


# --------------------------
# Funções de Livros
# --------------------------

def inserir_livro(titulo, autor, ano, isbn, quantidade):
    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT INTO livros (titulo, autor, ano, isbn, quantidade) VALUES (?, ?, ?, ?, ?)",
              (titulo, autor, ano, isbn, quantidade))
    conn.commit()
    conn.close()

def listar_livros():
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT * FROM livros")
    livros = c.fetchall()
    conn.close()
    return livros


# --------------------------
# Funções de Empréstimos
# --------------------------

def emprestar_livro(usuario_id, livro_id):
    conn = conectar()
    c = conn.cursor()

    c.execute("SELECT quantidade FROM livros WHERE id=?", (livro_id,))
    qtd = c.fetchone()
    if not qtd or qtd[0] <= 0:
        conn.close()
        return False

    data_hoje = datetime.now().strftime("%Y-%m-%d")
    prazo = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    c.execute("INSERT INTO emprestimos (usuario_id, livro_id, data_emprestimo, prazo_devolucao) VALUES (?, ?, ?, ?)",
              (usuario_id, livro_id, data_hoje, prazo))
    c.execute("UPDATE livros SET quantidade = quantidade - 1 WHERE id=?", (livro_id,))

    conn.commit()
    conn.close()
    return True

def listar_emprestimos_usuario(usuario_id):
    conn = conectar()
    c = conn.cursor()
    c.execute('''SELECT e.id, l.titulo, e.data_emprestimo, e.prazo_devolucao, e.devolvido
                 FROM emprestimos e
                 JOIN livros l ON e.livro_id = l.id
                 WHERE e.usuario_id = ?''', (usuario_id,))
    data = c.fetchall()
    conn.close()
    return data

def devolver_livro(emprestimo_id):
    conn = conectar()
    c = conn.cursor()
    c.execute("UPDATE emprestimos SET devolvido = 1 WHERE id=?", (emprestimo_id,))
    conn.commit()
    conn.close()

