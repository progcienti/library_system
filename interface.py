import tkinter as tk
from tkinter import ttk
from database import listar_livros
from user_views import tela_login_usuario, tela_registro, tela_usuario
from admin_views import tela_login_admin

def tela_inicial():
    root = tk.Tk()
    root.title("📚 Sistema de Biblioteca IFAC")
    root.geometry("900x500")

    # --- Barra superior ---
    top_frame = tk.Frame(root)
    top_frame.pack(side="top", fill="x", pady=10)

    tk.Button(top_frame, text="Login", command=lambda: tela_login_usuario(root)).pack(side="right", padx=5)
    tk.Button(top_frame, text="Registrar-se", command=lambda: tela_registro(root)).pack(side="right", padx=5)
    tk.Button(top_frame, text="Bibliotecário", command=lambda: tela_login_admin(root)).pack(side="right", padx=5)

    # --- Acervo de Livros ---
    tk.Label(root, text="Acervo da Biblioteca", font=("Arial", 18)).pack(pady=10)

    tabela = ttk.Treeview(root, columns=("id", "titulo", "autor", "ano", "isbn", "qtd"), show="headings")
    for col in tabela["columns"]:
        tabela.heading(col, text=col.capitalize())
    tabela.pack(fill="both", expand=True)

    for livro in listar_livros():
        tabela.insert("", "end", values=livro)

    root.mainloop()
