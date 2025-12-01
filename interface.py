import ttkbootstrap as tb
from ttkbootstrap.constants import *
import database as db
from user_views import tela_login_usuario, tela_registro, tela_login_admin
from datetime import datetime

def tela_inicial():
    root = tb.Window(themename="superhero")
    root.title("Biblioteca - System Library")
    root.geometry("1280x720")

    # ------------------ TOPO ------------------
    top = tb.Frame(root, padding=12)
    top.pack(fill='x')

    title = tb.Label(
        top,
        text="📚 BIBLIOTECA IFAC – ACERVO DIGITAL",
        font=("Segoe UI", 28, "bold"),
        bootstyle="inverse-primary"
    )
    title.pack(side='left', padx=10)

    # ------------------ BARRA DE PESQUISA ------------------
    frm_search = tb.Frame(top)
    frm_search.pack(side='right')

    e_search = tb.Entry(frm_search, width=40)
    e_search.pack(side='left', padx=(0, 6))

    cmb_filtro = tb.Combobox(
        frm_search,
        values=["Título", "Autor", "ISBN", "Tipo", "Ano"],
        width=12
    )
    cmb_filtro.set("Título")
    cmb_filtro.pack(side='left', padx=(0, 6))

    btn_buscar = tb.Button(frm_search, text="Buscar", bootstyle="info", width=10)
    btn_buscar.pack(side='left', padx=6)

    btn_limpar = tb.Button(frm_search, text="Limpar", bootstyle="secondary", width=10)
    btn_limpar.pack(side='left')

    # ------------------ TABELA ------------------
    content = tb.Frame(root, padding=12)
    content.pack(fill='both', expand=True, side='left')

    cols = ("ID", "Título", "Autor", "Ano", "ISBN", "Qtd", "Tipo")
    tree = tb.Treeview(content, columns=cols, show='headings', height=28)

    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor='center', width=160 if c == "Título" else 100)

    tree.pack(fill='both', expand=True, side='left')

    scroll = tb.Scrollbar(content, command=tree.yview)
    tree.configure(yscroll=scroll.set)
    scroll.pack(side='right', fill='y')

    # ------------------ NOVO PAINEL LATERAL MODERNO ------------------
    right = tb.Frame(root, padding=20, bootstyle="secondary")
    right.pack(side='right', fill='y')

    tb.Label(
        right,
        text="MENU DE AÇÕES",
        font=("Segoe UI", 20, "bold")
    ).pack(pady=(0, 15))

    tb.Button(
        right,
        text="Login de Usuário",
        bootstyle="info-outline",
        width=24,
        command=lambda: tela_login_usuario(root)
    ).pack(pady=6)

    tb.Button(
        right,
        text="Registrar Novo Usuário",
        bootstyle="success-outline",
        width=24,
        command=lambda: tela_registro(root)
    ).pack(pady=6)

    tb.Button(
        right,
        text="Login de Bibliotecário",
        bootstyle="danger-outline",
        width=24,
        command=lambda: tela_login_admin(root)
    ).pack(pady=6)

    tb.Separator(right).pack(fill='x', pady=18)

    # --------- CARDS ESTILIZADOS DE CONTAGEM ---------
    card_style = {"font": ("Segoe UI", 12, "bold")}

    lbl_total_livros = tb.Label(right, text="📚 Livros: --", **card_style)
    lbl_total_livros.pack(pady=5, anchor='w')

    lbl_total_usuarios = tb.Label(right, text="👤 Usuários: --", **card_style)
    lbl_total_usuarios.pack(pady=5, anchor='w')

    lbl_emprest_ativos = tb.Label(right, text="📦 Empréstimos: --", **card_style)
    lbl_emprest_ativos.pack(pady=5, anchor='w')

    lbl_atrasados = tb.Label(right, text="⚠️ Atrasados: --", **card_style)
    lbl_atrasados.pack(pady=5, anchor='w')

    lbl_multas = tb.Label(right, text="💰 Multas: R$ --", **card_style)
    lbl_multas.pack(pady=5, anchor='w')

    # ------------------ FUNÇÕES ------------------
    def carregar_acervo():
        for i in tree.get_children():
            tree.delete(i)
        rows = db.listar_livros()
        for r in rows:
            tree.insert("", "end", values=r)

        lbl_total_livros.config(text=f"📚 Livros: {db.contar_total_livros()}")
        lbl_total_usuarios.config(text=f"👤 Usuários: {db.contar_total_usuarios()}")
        lbl_emprest_ativos.config(text=f"📦 Empréstimos: {db.contar_emprestimos_ativos()}")
        lbl_atrasados.config(text=f"⚠️ Atrasados: {db.contar_atrasados()}")
        lbl_multas.config(text=f"💰 Multas: R$ {db.total_multas_geradas():.2f}")

    carregar_acervo()

    def aplicar_filtro():
        termo = e_search.get().strip().lower()
        tipo_filtro = cmb_filtro.get()

        for iid in tree.get_children():
            tree.delete(iid)

        rows = db.listar_livros()

        for r in rows:
            id_, titulo, autor, ano, isbn, qtd, tipo = r
            campo = {
                "Título": titulo,
                "Autor": autor,
                "ISBN": isbn,
                "Tipo": tipo,
                "Ano": str(ano)
            }.get(tipo_filtro, "")

            if termo in str(campo).lower():
                tree.insert("", "end", values=r)

    btn_buscar.configure(command=aplicar_filtro)
    btn_limpar.configure(command=lambda: (e_search.delete(0, 'end'), carregar_acervo()))

    root.mainloop()


if __name__ == "__main__":
    db.criar_tabelas()
    tela_inicial()
