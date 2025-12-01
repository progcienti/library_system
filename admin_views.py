import ttkbootstrap as tb
from ttkbootstrap.constants import *
import database as db
from tkinter import messagebox
from datetime import datetime
import reports

def tela_admin_painel(user_tuple):
    usuario_id, nome, login, tipo = user_tuple
    win = tb.Toplevel()
    win.title(f"Painel do Bibliotecário - {nome}")
    win.geometry("1150x720")

    notebook = tb.Notebook(win)
    notebook.pack(fill='both', expand=True)

    # Aba Dashboard resumo
    frm_dash = tb.Frame(notebook, padding=8)
    notebook.add(frm_dash, text="Dashboard")
    criar_cards_dashboard(frm_dash)

    # Aba Gerenciar Livros
    frm_livros = tb.Frame(notebook, padding=8)
    notebook.add(frm_livros, text="Gerenciar Livros")
    criar_gerenciador_livros(frm_livros)

    # Aba Empréstimos (visão geral)
    frm_emp = tb.Frame(notebook, padding=8)
    notebook.add(frm_emp, text="Empréstimos")
    criar_visao_emprestimos(frm_emp)

    # Aba Relatórios
    frm_reports = tb.Frame(notebook, padding=8)
    notebook.add(frm_reports, text="Relatórios")
    tb.Label(frm_reports, text="Relatórios disponíveis", font=("Segoe UI", 14, "bold")).pack(pady=8)
    tb.Button(frm_reports, text="Mais emprestados (gráfico)", bootstyle="info", command=reports.gerar_relatorio_mais_emprestados).pack(pady=6)

def criar_cards_dashboard(parent):
    frame = tb.Frame(parent, padding=12)
    frame.pack(fill='x')
    # cards em linha
    total_livros = db.contar_total_livros()
    total_usuarios = db.contar_total_usuarios()
    emprest_ativos = db.contar_emprestimos_ativos()
    atrasados = db.contar_atrasados()
    total_multas = db.total_multas_geradas()

    tb.Label(frame, text=f"Livros: {total_livros}", font=("Segoe UI", 14, "bold")).pack(side='left', padx=12)
    tb.Label(frame, text=f"Usuários: {total_usuarios}", font=("Segoe UI", 14, "bold")).pack(side='left', padx=12)
    tb.Label(frame, text=f"Empréstimos ativos: {emprest_ativos}", font=("Segoe UI", 14, "bold")).pack(side='left', padx=12)
    tb.Label(frame, text=f"Atrasados: {atrasados}", font=("Segoe UI", 14, "bold")).pack(side='left', padx=12)
    tb.Label(frame, text=f"Total multas: R$ {total_multas:.2f}", font=("Segoe UI", 14, "bold")).pack(side='left', padx=12)

def criar_gerenciador_livros(parent):
    cols = ("ID", "Título", "Autor", "Ano", "ISBN", "Qtd", "Tipo")
    tree = tb.Treeview(parent, columns=cols, show='headings', height=18)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor='center', width=160 if c == "Título" else 100)
    tree.pack(fill='both', expand=True, side='left', padx=6, pady=6)

    scr = tb.Scrollbar(parent, orient='vertical', command=tree.yview)
    tree.configure(yscroll=scr.set)
    scr.pack(side='right', fill='y')

    def carregar():
        for i in tree.get_children():
            tree.delete(i)
        for r in db.listar_livros():
            tree.insert("", "end", values=r)

    # formulário para adicionar/editar
    frm = tb.Frame(parent, padding=8)
    frm.pack(fill='x')

    tb.Label(frm, text="Título").grid(row=0, column=0, padx=4, pady=4, sticky='w')
    e_titulo = tb.Entry(frm, width=50); e_titulo.grid(row=0, column=1, pady=4, sticky='w')

    tb.Label(frm, text="Autor").grid(row=1, column=0, padx=4, pady=4, sticky='w')
    e_autor = tb.Entry(frm, width=40); e_autor.grid(row=1, column=1, pady=4, sticky='w')

    tb.Label(frm, text="Ano").grid(row=2, column=0, padx=4, pady=4, sticky='w')
    e_ano = tb.Entry(frm, width=12); e_ano.grid(row=2, column=1, pady=4, sticky='w')

    tb.Label(frm, text="ISBN").grid(row=3, column=0, padx=4, pady=4, sticky='w')
    e_isbn = tb.Entry(frm, width=25); e_isbn.grid(row=3, column=1, pady=4, sticky='w')

    tb.Label(frm, text="Quantidade").grid(row=4, column=0, padx=4, pady=4, sticky='w')
    e_qtd = tb.Entry(frm, width=8); e_qtd.grid(row=4, column=1, pady=4, sticky='w')
    e_qtd.insert(0, "1")

    tb.Label(frm, text="Tipo").grid(row=5, column=0, padx=4, pady=4, sticky='w')
    e_tipo = tb.Entry(frm, width=30); e_tipo.grid(row=5, column=1, pady=4, sticky='w')
    e_tipo.insert(0, "Geral")

    def adicionar():
        titulo = e_titulo.get().strip()
        autor = e_autor.get().strip()
        ano = e_ano.get().strip()
        isbn = e_isbn.get().strip()
        qtd = e_qtd.get().strip()
        tipo = e_tipo.get().strip() or "Geral"
        if not titulo:
            messagebox.showwarning("Aviso", "Título é obrigatório.")
            return
        try:
            ano_i = int(ano) if ano else None
            qtd_i = int(qtd)
        except ValueError:
            messagebox.showerror("Erro", "Ano e quantidade devem ser números.")
            return
        db.inserir_livro(titulo, autor, ano_i, isbn, qtd_i, tipo)
        messagebox.showinfo("Sucesso", "Livro cadastrado.")
        carregar()

    def remover():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um livro para remover.")
            return
        livro_id = tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", "Remover esse livro?"):
            db.remover_livro(livro_id)
            carregar()

    def editar():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um livro para editar.")
            return
        livro = tree.item(sel[0])['values']
        # preencher campos
        e_titulo.delete(0,'end'); e_titulo.insert(0, livro[1])
        e_autor.delete(0,'end'); e_autor.insert(0, livro[2])
        e_ano.delete(0,'end'); e_ano.insert(0, livro[3] or "")
        e_isbn.delete(0,'end'); e_isbn.insert(0, livro[4] or "")
        e_qtd.delete(0,'end'); e_qtd.insert(0, livro[5])
        e_tipo.delete(0,'end'); e_tipo.insert(0, livro[6] or "Geral")
        # alterar botão adicionar para salvar edição
        def salvar_edicao():
            try:
                ano_i = int(e_ano.get()) if e_ano.get() else None
                qtd_i = int(e_qtd.get())
            except ValueError:
                messagebox.showerror("Erro", "Ano/quantidade inválidos.")
                return
            db.atualizar_livro(livro[0], e_titulo.get().strip(), e_autor.get().strip(), ano_i, e_isbn.get().strip(), qtd_i, e_tipo.get().strip() or "Geral")
            messagebox.showinfo("Sucesso", "Livro atualizado.")
            carregar()
            btn_salvar.grid_forget()
            btn_adicionar.grid(row=6, column=1, pady=8, sticky='w')

        btn_adicionar.grid_forget()
        btn_salvar.grid(row=6, column=1, pady=8, sticky='w')

        btn_salvar.configure(command=salvar_edicao)

    btn_adicionar = tb.Button(frm, text="Adicionar Livro", bootstyle="success", command=adicionar)
    btn_adicionar.grid(row=6, column=1, pady=8, sticky='w')
    btn_remover = tb.Button(frm, text="Remover Selecionado", bootstyle="danger", command=remover)
    btn_remover.grid(row=6, column=1, pady=8, sticky='e')
    btn_editar = tb.Button(frm, text="Editar Selecionado", bootstyle="warning", command=editar)
    btn_editar.grid(row=6, column=0, pady=8, sticky='w')
    btn_salvar = tb.Button(frm, text="Salvar Edição", bootstyle="primary")

    carregar()

def criar_visao_emprestimos(parent):
    cols_emp = ("ID", "Usuário", "Título", "Tipo", "Data Empréstimo", "Prazo", "Devolvido", "Data Devolução", "Multa")
    tree_emp = tb.Treeview(parent, columns=cols_emp, show='headings', height=18)
    for c in cols_emp:
        tree_emp.heading(c, text=c)
        tree_emp.column(c, anchor='center', width=140 if c == "Título" else 110)
    tree_emp.pack(fill='both', expand=True, side='left', padx=6, pady=6)

    scr_emp = tb.Scrollbar(parent, orient='vertical', command=tree_emp.yview)
    tree_emp.configure(yscroll=scr_emp.set)
    scr_emp.pack(side='right', fill='y')

    def formatar_data_iso(data_iso):
        if not data_iso:
            return "—"
        try:
            return datetime.fromisoformat(data_iso).strftime("%Y-%m-%d")
        except Exception:
            return data_iso[:10]

    def carregar_emprestimos():
        for i in tree_emp.get_children():
            tree_emp.delete(i)
        rows = db.listar_emprestimos_ativos()
        for r in rows:
            id_e, nome_u, titulo, tipo_livro, emprestimo, prazo, devolvido, data_dev, multa = r
            d_emp = formatar_data_iso(emprestimo)
            d_prazo = formatar_data_iso(prazo)
            d_dev = formatar_data_iso(data_dev) if data_dev else "—"
            devolvido_txt = "Sim" if devolvido else "Não"
            tree_emp.insert("", "end", values=(id_e, nome_u, titulo, tipo_livro, d_emp, d_prazo, devolvido_txt, d_dev, f"{multa:.2f}"))

    tb.Button(parent, text="Atualizar Lista", bootstyle="secondary", command=carregar_emprestimos).pack(pady=6)
    carregar_emprestimos()
