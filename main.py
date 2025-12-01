import database as db
from interface import tela_inicial

if __name__ == "__main__":
    db.criar_tabelas()
    tela_inicial()
