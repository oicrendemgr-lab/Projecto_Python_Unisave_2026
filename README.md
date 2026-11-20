Sistema de Gestão de Stock para Pequenas Lojas

Sistema desenvolvido em Python para ajudar pequenas lojas, mercearias e minimercados a controlar os seus produtos, quantidades, preços e vendas. O projeto procura resolver dificuldades de organização do stock, reduzir erros no registo manual e facilitar o acompanhamento dos produtos disponíveis.

Elementos do Grupo

1. Flávio Sebastião Nhacuonga(nhacuongaflavio31-wq!)
2. Ednercio Castro Gujamo (oicrendemgr-lab)

Funcionalidades

- Registar novos produtos com nome, categoria, preço e quantidade.
- Listar e pesquisar produtos registados.
- Atualizar preços e quantidades.
- Registar vendas e atualizar automaticamente o stock.
- Impedir vendas superiores à quantidade disponível.
- Identificar produtos com stock baixo.
- Consultar o resumo e o valor total das vendas.
- Guardar os dados permanentemente em ficheiros JSON.

Stack Técnica

- Linguagem: Python 3.x
- Paradigma: Programação Orientada a Objetos (POO)
- Armazenamento: JSON
- Dependências: Bibliotecas padrão do Python, incluindo "json", "datetime", "pathlib" e "dataclasses".

Arquitetura

O projeto está organizado em módulos:

- "main.py": contém o menu principal e a interação com o utilizador.
- "models.py": contém a classe Produto e a representação dos produtos.
- "servicos.py": implementa as operações de gestão de produtos, stock e vendas.
- "armazenamento.py": gere a leitura e gravação dos dados em JSON.
- "dados/produtos.json": armazena os produtos.
- "dados/vendas.json": armazena o histórico de vendas.

Requisitos

Python 3.8 ou superior instalado no computador.

Instalação e Execução

git clone https://github.com/oicrendemgr-lab/Projecto_Python_Unisave_2026.git
cd Projecto_Python_Unisave_2026
python main.py