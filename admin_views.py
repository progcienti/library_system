import tkinter as tk
from tkinter import messagebox, ttk
from database import verificar_login, listar_livros, inserir_livro

def tela_login_admin(root):
    win = tk.Toplevel(root)
    win.title("Login Bibliotecário")
    win.geometry("300x200")

    tk.Label(win, text="Login").pack()
    e_login = tk.Entry(win)
    e_login.pack()

    tk.Label(win, text="Senha").pack()
    e_senha = tk.Entry(win, show="*")
    e_senha.pack()

    def logar():
        user = verificar_login(e_login.get(), e_senha.get())
        if user and user[6] == "admin":
            messagebox.showinfo("Sucesso", "Bem-vindo, Bibliotecário!")
            win.destroy()
            tela_admin()
        else:
            messagebox.showerror("Erro", "Acesso negado.")

    tk.Button(win, text="Entrar", command=logar).pack(pady=10)


def tela_admin():
    win = tk.Toplevel()
    win.title("Painel do Bibliotecário")
    win.geometry("800x500")

    notebook = ttk.Notebook(win)
    frame_livros = ttk.Frame(notebook)
    notebook.add(frame_livros, text="Gerenciar Livros")
    notebook.pack(expand=True, fill="both")

    tk.Label(frame_livros, text="Cadastrar Novo Livro").pack(pady=5)

    e_titulo = tk.Entry(frame_livros)
    e_titulo.insert(0, "Título")
    e_titulo.pack()

    e_autor = tk.Entry(frame_livros)
    e_autor.insert(0, "Autor")
    e_autor.pack()

    e_ano = tk.Entry(frame_livros)
    e_ano.insert(0, "Ano")
    e_ano.pack()

    e_isbn = tk.Entry(frame_livros)
    e_isbn.insert(0, "ISBN")
    e_isbn.pack()

    e_qtd = tk.Entry(frame_livros)
    e_qtd.insert(0, "Quantidade")
    e_qtd.pack()

    def salvar():
        inserir_livro(e_titulo.get(), e_autor.get(), e_ano.get(), e_isbn.get(), e_qtd.get())
        messagebox.showinfo("Sucesso", "Livro cadastrado!")
        atualizar()

    tk.Button(frame_livros, text="Salvar Livro", command=salvar).pack(pady=5)

    tabela = ttk.Treeview(frame_livros, columns=("id", "titulo", "autor", "ano", "isbn", "qtd"), show="headings")
    for col in tabela["columns"]:
        tabela.heading(col, text=col.capitalize())
    tabela.pack(fill="both", expand=True)

    def atualizar():
        for i in tabela.get_children():
            tabela.delete(i)
        for l in listar_livros():
            tabela.insert("", "end", values=l)

    atualizar()
