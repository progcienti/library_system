# System Library

Um sistema de gestão e controle de uma biblioteca, na qual controlará todo o fluxo de livros novos, antigos, empréstimos, devoluções, com um banco de dados com os usuários e os livros disponíveis. Ele permitirá o cadastro de novos livros e gerenciar todo o restante.

## Requisitos
- Python 3.8+
- pip
- Instalar dependências:


## Arquivos principais
- database.py
- models.py
- interface.py
- user_views.py
- admin_views.py
- reports.py
- main.py
- pasta `data/` (será criada automaticamente)

## Admin padrão
- usuário: `admin`
- senha: `1234`

## Observações
- Datas são salvas em ISO (UTC) no banco, exibidas em formato `YYYY-MM-DD`.
