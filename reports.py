import database as db
import matplotlib.pyplot as plt

def gerar_relatorio_mais_emprestados():
    df = db.relatorio_mais_emprestados(limit=10)
    if df.empty:
        print("Sem dados para relatório.")
        return
    ax = df.plot(kind='bar', x='titulo', y='total', legend=False)
    ax.set_xlabel("Título")
    ax.set_ylabel("Total de Empréstimos")
    ax.set_title("Livros Mais Emprestados")
    plt.tight_layout()
    plt.show()
