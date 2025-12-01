import ttkbootstrap as tb
from ttkbootstrap.constants import *
import database as db
from tkinter import messagebox
from datetime import datetime

def tela_registro(master):
    win = tb.Toplevel(master)
    win.title("Registrar Usuário")
    win.geometry("380x320")
    frm = tb.Frame(win, padding=12)
    frm.pack(fill='both', expand=True)

    tb.Label(frm, text="Nome:").pack(anchor='w')
    e_nome = tb.Entry(frm)
    e_nome.pack(fill='x')

    tb.Label(frm, text="Email:").pack(anchor='w')
    e_email = tb.Entry(frm)
    e_email.pack(fill='x')

    tb.Label(frm, text="Login:").pack(anchor='w')
    e_login = tb.Entry(frm)
    e_login.pack(fill='x')

    tb.Label(frm, text="Senha:").pack(anchor='w')
    e_senha = tb.Entry(frm, show="*")
    e_senha.pack(fill='x')

    def registrar_action():
        nome = e_nome.get().strip()
        email = e_email.get().strip()
        login = e_login.get().strip()
        senha = e_senha.get().strip()
        if not nome or not login or not senha:
            messagebox.showwarning("Aviso", "Preencha nome, login e senha.")
            return
        ok, err = db.inserir_usuario(nome, email, login, senha, tipo="user")
        if ok:
            messagebox.showinfo("Sucesso", "Usuário registrado.")
            win.destroy()
        else:
            messagebox.showerror("Erro", f"Não foi possível registrar: {err}")

    tb.Button(frm, text="Registrar", bootstyle="success", command=registrar_action).pack(pady=10)

def tela_login_usuario(master):
    win = tb.Toplevel(master)
    win.title("Login Usuário")
    win.geometry("360x240")
    frm = tb.Frame(win, padding=12)
    frm.pack(fill='both', expand=True)

    tb.Label(frm, text="Login:").pack(anchor='w')
    e_login = tb.Entry(frm)
    e_login.pack(fill='x')

    tb.Label(frm, text="Senha:").pack(anchor='w')
    e_senha = tb.Entry(frm, show="*")
    e_senha.pack(fill='x')

    def entrar():
        login = e_login.get().strip()
        senha = e_senha.get().strip()
        user = db.verificar_login(login, senha)
        if not user:
            messagebox.showerror("Erro", "Login ou senha inválidos.")
            return
        if user[3] == "admin":
            messagebox.showwarning("Aviso", "Este é um usuário admin. Use a tela de bibliotecário.")
            return
        win.destroy()
        tela_usuario(user)

    tb.Button(frm, text="Entrar", bootstyle="primary", command=entrar).pack(pady=8)

def tela_login_admin(master):
    win = tb.Toplevel(master)
    win.title("Login Bibliotecário")
    win.geometry("360x240")
    frm = tb.Frame(win, padding=12)
    frm.pack(fill='both', expand=True)

    tb.Label(frm, text="Login:").pack(anchor='w')
    e_login = tb.Entry(frm)
    e_login.pack(fill='x')

    tb.Label(frm, text="Senha:").pack(anchor='w')
    e_senha = tb.Entry(frm, show="*")
    e_senha.pack(fill='x')

    def entrar():
        login = e_login.get().strip()
        senha = e_senha.get().strip()
        user = db.verificar_login(login, senha)
        if not user:
            messagebox.showerror("Erro", "Login ou senha inválidos.")
            return
        if user[3] != "admin":
            messagebox.showwarning("Aviso", "Usuário não é bibliotecário.")
            return
        win.destroy()
        from admin_views import tela_admin_painel
        tela_admin_painel(user)

    tb.Button(frm, text="Entrar", bootstyle="primary", command=entrar).pack(pady=8)

# ------------------ Tela principal do usuário ------------------
def tela_usuario(user_tuple):
    usuario_id, nome, login, tipo = user_tuple
    win = tb.Toplevel()
    win.title(f"Biblioteca - Usuário: {nome}")
    win.geometry("1000x650")

    notebook = tb.Notebook(win)
    notebook.pack(fill='both', expand=True)

    # Aba Acervo
    frm_acervo = tb.Frame(notebook, padding=8)
    notebook.add(frm_acervo, text="Acervo")

    cols = ("ID", "Título", "Autor", "Ano", "ISBN", "Qtd", "Tipo")
    tree = tb.Treeview(frm_acervo, columns=cols, show='headings', height=18)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=140 if c == "Título" else 90, anchor='center')
    tree.pack(fill='both', expand=True, side='left', padx=6, pady=6)

    scroll = tb.Scrollbar(frm_acervo, orient='vertical', command=tree.yview)
    tree.configure(yscroll=scroll.set)
    scroll.pack(side='right', fill='y')

    def carregar_acervo():
        for i in tree.get_children():
            tree.delete(i)
        for r in db.listar_livros():
            tree.insert("", "end", values=r)

    carregar_acervo()

    def emprestar():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um livro.")
            return
        livro_id = tree.item(sel[0])['values'][0]
        ok, err = db.emprestar_livro(usuario_id, livro_id)
        if ok:
            messagebox.showinfo("Sucesso", "Livro emprestado com sucesso.")
            carregar_acervo()
            atualizar_emprestimos()
        else:
            messagebox.showerror("Erro", err)

    tb.Button(frm_acervo, text="Emprestar Livro", bootstyle="success-outline", command=emprestar).pack(pady=6)

    # Aba Meus Empréstimos / Histórico
    frm_emprest = tb.Frame(notebook, padding=8)
    notebook.add(frm_emprest, text="Meus Empréstimos / Histórico")

    cols2 = ("ID", "Título", "Tipo", "Data Empréstimo", "Prazo", "Devolvido", "Data Devolução", "Dias Atraso", "Multa (R$)")
    tree2 = tb.Treeview(frm_emprest, columns=cols2, show='headings', height=18)
    for c in cols2:
        tree2.heading(c, text=c)
        tree2.column(c, anchor='center', width=120)
    tree2.pack(fill='both', expand=True, side='left', padx=6, pady=6)

    scroll2 = tb.Scrollbar(frm_emprest, orient='vertical', command=tree2.yview)
    tree2.configure(yscroll=scroll2.set)
    scroll2.pack(side='right', fill='y')

    def formatar_data_iso(data_iso):
        if not data_iso:
            return "—"
        try:
            return datetime.fromisoformat(data_iso).strftime("%Y-%m-%d")
        except Exception:
            return data_iso[:10]

    def calcular_dias_e_multa(prazo_iso, data_devolucao_iso):
        agora = datetime.utcnow()
        try:
            prazo = datetime.fromisoformat(prazo_iso)
        except Exception:
            return 0, 0.0
        if data_devolucao_iso:
            try:
                data_dev = datetime.fromisoformat(data_devolucao_iso)
            except Exception:
                data_dev = agora
        else:
            data_dev = agora
        dias = (data_dev.date() - prazo.date()).days
        dias_atraso = dias if dias > 0 else 0
        multa = dias_atraso * db.get_multa_por_dia()
        return dias_atraso, round(multa, 2)

    def atualizar_emprestimos():
        for i in tree2.get_children():
            tree2.delete(i)
        rows = db.listar_emprestimos_usuario(usuario_id)
        for r in rows:
            id_e, titulo, tipo_livro, emprestimo, prazo, devolvido, data_devolucao, multa, isbn = r
            d_emp = formatar_data_iso(emprestimo)
            d_prazo = formatar_data_iso(prazo)
            d_dev = formatar_data_iso(data_devolucao) if data_devolucao else "—"
            dias_atraso, multa_calc = calcular_dias_e_multa(prazo, data_devolucao)
            # preferir multa registrada ao calcular novamente (se devolvido)
            multa_exibir = f"{multa:.2f}" if multa and multa > 0 else f"{multa_calc:.2f}"
            devolvido_txt = "Sim" if devolvido else "Não"
            tree2.insert("", "end", values=(id_e, titulo, tipo_livro, d_emp, d_prazo, devolvido_txt, d_dev, dias_atraso, multa_exibir))

    atualizar_emprestimos()

    def devolver():
        sel = tree2.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um empréstimo.")
            return
        emp_id = tree2.item(sel[0])['values'][0]
        # buscar prazo
        rows = db.listar_emprestimos_usuario(usuario_id)
        linha = next((r for r in rows if r[0] == emp_id), None)
        if not linha:
            messagebox.showerror("Erro", "Empréstimo não encontrado.")
            return
        _, _, _, _, prazo_iso, devolvido, data_dev, multa_reg, _ = linha
        if devolvido:
            messagebox.showinfo("Info", "Este empréstimo já foi devolvido.")
            atualizar_emprestimos()
            return
        # calcular multa
        agora = datetime.utcnow()
        try:
            prazo = datetime.fromisoformat(prazo_iso)
        except Exception:
            prazo = agora
        dias_atraso = (agora.date() - prazo.date()).days
        dias_atraso = dias_atraso if dias_atraso > 0 else 0
        multa = round(dias_atraso * db.get_multa_por_dia(), 2)
        confirm = messagebox.askyesno("Confirmar Devolução", f"Dias de atraso: {dias_atraso}\nMulta: R$ {multa:.2f}\n\nConfirmar devolução?")
        if not confirm:
            return
        ok, err = db.devolver_livro(emp_id, multa_calculada=multa)
        if ok:
            messagebox.showinfo("Sucesso", f"Devolução registrada. Multa: R$ {multa:.2f}")
            atualizar_emprestimos()
            carregar_acervo()
        else:
            messagebox.showerror("Erro", err)

    tb.Button(frm_emprest, text="Devolver Livro", bootstyle="danger-outline", command=devolver).pack(pady=6)
    tb.Button(frm_emprest, text="Atualizar Lista", bootstyle="secondary", command=atualizar_emprestimos).pack(pady=4)
