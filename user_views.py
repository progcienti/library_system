import tkinter as tk
from tkinter import messagebox, ttk
from database import inserir_usuario, verificar_login, listar_livros, emprestar_livro, listar_emprestimos_usuario, devolver_livro

def tela_registro(root):
    win = tk.Toplevel(root)
    win.title("Registrar Usuário")
    win.geometry("300x300")

    tk.Label(win, text="Nome").pack()
    e_nome = tk.Entry(win)
    e_nome.pack()

    tk.Label(win, text="Email").pack()
    e_email = tk.Entry(win)
    e_email.pack()

    tk.Label(win, text="Login").pack()
    e_login = tk.Entry(win)
    e_login.pack()

    tk.Label(win, text="Senha").pack()
    e_senha = tk.Entry(win, show="*")
    e_senha.pack()

    def registrar():
        inserir_usuario(e_nome.get(), e_email.get(), e_login.get(), e_senha.get())
        messagebox.showinfo("Sucesso", "Usuário registrado com sucesso!")
        win.destroy()

    tk.Button(win, text="Registrar", command=registrar).pack(pady=10)


def tela_login_usuario(root):
    win = tk.Toplevel(root)
    win.title("Login Usuário")
    win.geometry("300x200")

    tk.Label(win, text="Login").pack()
    e_login = tk.Entry(win)
    e_login.pack()

    tk.Label(win, text="Senha").pack()
    e_senha = tk.Entry(win, show="*")
    e_senha.pack()

    def logar():
        user = verificar_login(e_login.get(), e_senha.get())
        if user:
            if user[6] == "admin":
                messagebox.showwarning("Aviso", "Use o login de Bibliotecário.")
            else:
                messagebox.showinfo("Sucesso", f"Bem-vindo, {user[1]}!")
                win.destroy()
                tela_usuario(user)
        else:
            messagebox.showerror("Erro", "Login ou senha incorretos.")

    tk.Button(win, text="Entrar", command=logar).pack(pady=10)


def tela_usuario(user):
    win = tk.Toplevel()
    win.title(f"Biblioteca - Usuário: {user[1]}")
    win.geometry("800x500")

    tk.Label(win, text=f"Bem-vindo, {user[1]}", font=("Arial", 16)).pack(pady=10)

    notebook = ttk.Notebook(win)
    frame_acervo = ttk.Frame(notebook)
    frame_emprestimos = ttk.Frame(notebook)
    notebook.add(frame_acervo, text="Acervo")
    notebook.add(frame_emprestimos, text="Meus Empréstimos")
    notebook.pack(expand=True, fill="both")

    # Acervo
    livros = listar_livros()
    tabela = ttk.Treeview(frame_acervo, columns=("id", "titulo", "autor", "ano", "isbn", "qtd"), show="headings")
    for col in tabela["columns"]:
        tabela.heading(col, text=col.capitalize())
    tabela.pack(fill="both", expand=True)

    for l in livros:
        tabela.insert("", "end", values=l)

    def pegar_livro():
        item = tabela.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um livro.")
            return
        livro_id = tabela.item(item)["values"][0]
        if emprestar_livro(user[0], livro_id):
            messagebox.showinfo("Sucesso", "Livro emprestado!")
        else:
            messagebox.showerror("Erro", "Livro indisponível.")

    tk.Button(frame_acervo, text="Emprestar Livro", command=pegar_livro).pack(pady=5)

    # Empréstimos
    tabela_emp = ttk.Treeview(frame_emprestimos, columns=("id", "titulo", "emprestimo", "prazo", "devolvido"), show="headings")
    for col in tabela_emp["columns"]:
        tabela_emp.heading(col, text=col.capitalize())
    tabela_emp.pack(fill="both", expand=True)

    def atualizar_emprestimos():
        for i in tabela_emp.get_children():
            tabela_emp.delete(i)
        for e in listar_emprestimos_usuario(user[0]):
            tabela_emp.insert("", "end", values=e)

    def devolver():
        item = tabela_emp.focus()
        if not item:
            return
        emp_id = tabela_emp.item(item)["values"][0]
        devolver_livro(emp_id)
        messagebox.showinfo("Devolvido", "Livro devolvido com sucesso!")
        atualizar_emprestimos()

    tk.Button(frame_emprestimos, text="Atualizar Lista", command=atualizar_emprestimos).pack(pady=5)
    tk.Button(frame_emprestimos, text="Devolver Livro", command=devolver).pack(pady=5)
