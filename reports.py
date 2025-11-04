import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

def relatorio_mais_emprestados():
    conn = sqlite3.connect("data/library.db")
    df = pd.read_sql_query('''
        SELECT livros.titulo, COUNT(emprestimos.id) AS total
        FROM emprestimos
        JOIN livros ON emprestimos.livro_id = livros.id
        GROUP BY livros.titulo
        ORDER BY total DESC
    ''', conn)
    df.plot(kind='bar', x='titulo', y='total', title='Livros Mais Emprestados')
    plt.show()
