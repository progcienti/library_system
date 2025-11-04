class Livro:
    def __init__(self, titulo, autor, ano, isbn, quantidade):
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.isbn = isbn
        self.quantidade = quantidade


class Usuario:
    def __init__(self, nome, email, telefone, data_adesao):
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.data_adesao = data_adesao


class Emprestimo:
    def __init__(self, usuario, livro, data_emprestimo, prazo_devolucao):
        self.usuario = usuario
        self.livro = livro
        self.data_emprestimo = data_emprestimo
        self.prazo_devolucao = prazo_devolucao
