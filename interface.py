import tkinter as tk
from tkinter import messagebox

def abrir_interface():
    janela = tk.Tk()
    janela.title("Library System")
    janela.geometry("400x300")

    tk.Label(janela, text="Sistema de Biblioteca", font=("Arial", 16)).pack(pady=20)
    tk.Button(janela, text="Cadastrar Livro").pack(pady=5)
    tk.Button(janela, text="Cadastrar Usuário").pack(pady=5)
    tk.Button(janela, text="Emprestar Livro").pack(pady=5)
    tk.Button(janela, text="Devolver Livro").pack(pady=5)
    tk.Button(janela, text="Sair", command=janela.destroy).pack(pady=10)

    janela.mainloop()
