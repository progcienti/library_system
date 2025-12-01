from dataclasses import dataclass

@dataclass
class Livro:
    id: int
    titulo: str
    autor: str
    ano: int
    isbn: str
    qtd: int
    tipo: str

@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    login: str
    tipo: str
