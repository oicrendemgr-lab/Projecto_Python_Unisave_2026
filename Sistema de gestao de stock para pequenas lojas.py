"""
PROJECTO: Sistema de Gestão de Stock para Pequenas Lojas
DISCIPLINA: Programação I
LINGUAGEM: Python 3.x
PARADIGMA: Programação Orientada a Objectos

Aplicação gráfica desenvolvida com Tkinter.
Os dados são guardados em ficheiros JSON.
"""

import json
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class Produto:
    def __init__(self, codigo, nome, categoria, preco, quantidade, limite_stock):
        self.codigo = codigo
        self.nome = nome
        self.categoria = categoria
        self.preco = preco
        self.quantidade = quantidade
        self.limite_stock = limite_stock

    def para_dicionario(self):
        return {
            "codigo": self.codigo,
            "nome": self.nome,
            "categoria": self.categoria,
            "preco": self.preco,
            "quantidade": self.quantidade,
            "limite_stock": self.limite_stock
        }


class SistemaStock:
    def __init__(self):
        self.pasta = Path("dados")
        self.pasta.mkdir(exist_ok=True)

        self.ficheiro_produtos = self.pasta / "produtos.json"
        self.ficheiro_vendas = self.pasta / "vendas.json"

        self.criar_ficheiros()

    def criar_ficheiros(self):
        for ficheiro in [self.ficheiro_produtos, self.ficheiro_vendas]:
            if not ficheiro.exists():
                ficheiro.write_text("[]", encoding="utf-8")

    def carregar(self, ficheiro):
        try:
            with ficheiro.open("r", encoding="utf-8") as f:
                dados = json.load(f)

            if not isinstance(dados, list):
                raise ValueError("Formato de dados inválido.")

            return dados

        except json.JSONDecodeError:
            raise ValueError(f"O ficheiro {ficheiro} contém dados inválidos.")

    def guardar(self, ficheiro, dados):
        temporario = ficheiro.with_suffix(".tmp")

        with temporario.open("w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

        temporario.replace(ficheiro)

    def registar_produto(self, nome, categoria, preco, quantidade, limite):
        produtos = self.carregar(self.ficheiro_produtos)

        numero = max(
            [int(p["codigo"][1:]) for p in produtos
             if p.get("codigo", "").startswith("P")
             and p["codigo"][1:].isdigit()] + [0]
        ) + 1

        codigo = f"P{numero:04d}"

        produto = Produto(
            codigo, nome, categoria, preco, quantidade, limite
        )

        produtos.append(produto.para_dicionario())
        self.guardar(self.ficheiro_produtos, produtos)

        return codigo

    def listar_produtos(self):
        return self.carregar(self.ficheiro_produtos)

    def actualizar_produto(self, codigo, nome, categoria, preco, quantidade, limite):
        produtos = self.carregar(self.ficheiro_produtos)

        for p in produtos:
            if p["codigo"] == codigo:
                p["nome"] = nome
                p["categoria"] = categoria
                p["preco"] = preco
                p["quantidade"] = quantidade
                p["limite_stock"] = limite

                self.guardar(self.ficheiro_produtos, produtos)
                return True

        return False

    def registar_venda(self, codigo, quantidade):
        produtos = self.carregar(self.ficheiro_produtos)
        vendas = self.carregar(self.ficheiro_vendas)

        for p in produtos:
            if p["codigo"] == codigo:

                if quantidade <= 0:
                    raise ValueError("A quantidade deve ser superior a zero.")

                if quantidade > p["quantidade"]:
                    raise ValueError("Stock insuficiente.")

                total = quantidade * p["preco"]

                venda = {
                    "codigo_produto": codigo,
                    "nome_produto": p["nome"],
                    "quantidade": quantidade,
                    "preco_unitario": p["preco"],
                    "total": total,
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }

                p["quantidade"] -= quantidade
                vendas.append(venda)

                self.guardar(self.ficheiro_produtos, produtos)
                self.guardar(self.ficheiro_vendas, vendas)

                return venda

        raise ValueError("Produto não encontrado.")

    def produtos_stock_baixo(self):
        produtos = self.listar_produtos()

        return [
            p for p in produtos
            if p["quantidade"] <= p["limite_stock"]
        ]

    def resumo_vendas(self):
        vendas = self.carregar(self.ficheiro_vendas)

        return {
            "numero_vendas": len(vendas),
            "unidades": sum(v["quantidade"] for v in vendas),
            "total": sum(v["total"] for v in vendas),
            "vendas": vendas
        }


class AplicacaoStock:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Sistema de Gestão de Stock")
        self.janela.geometry("1050x700")
        self.janela.minsize(850, 600)

        self.sistema = SistemaStock()
        self.codigo_seleccionado = None

        self.criar_interface()
        self.actualizar_tabela()

    def criar_interface(self):
        # Cabeçalho
        cabecalho = tk.Frame(self.janela, bg="#17365D", height=85)
        cabecalho.pack(fill="x")
        cabecalho.pack_propagate(False)

        tk.Label(
            cabecalho,
            text="SISTEMA DE GESTÃO DE STOCK",
            font=("Arial", 21, "bold"),
            bg="#17365D",
            fg="white"
        ).pack(pady=8)

        tk.Label(
            cabecalho,
            text="Gestão de produtos, vendas e inventário",
            font=("Arial", 10),
            bg="#17365D",
            fg="white"
        ).pack()

        # Área principal
        principal = tk.Frame(self.janela, padx=15, pady=12)
        principal.pack(fill="both", expand=True)

        # Formulário
        formulario = tk.LabelFrame(
            principal,
            text="Dados do produto",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=10
        )
        formulario.pack(fill="x", pady=(0, 10))

        self.entrada_nome = self.criar_campo(formulario, "Nome:", 0, 0)
        self.entrada_categoria = self.criar_campo(formulario, "Categoria:", 0, 2)
        self.entrada_preco = self.criar_campo(formulario, "Preço (MT):", 1, 0)
        self.entrada_quantidade = self.criar_campo(formulario, "Quantidade:", 1, 2)
        self.entrada_limite = self.criar_campo(formulario, "Stock mínimo:", 2, 0)

        # Botões do formulário
        botoes = tk.Frame(formulario)
        botoes.grid(row=2, column=2, padx=5, pady=8, sticky="w")

        ttk.Button(
            botoes, text="Registar produto",
            command=self.registar
        ).pack(side="left", padx=3)

        ttk.Button(
            botoes, text="Actualizar",
            command=self.actualizar
        ).pack(side="left", padx=3)

        ttk.Button(
            botoes, text="Limpar",
            command=self.limpar_campos
        ).pack(side="left", padx=3)

        # Pesquisa
        pesquisa_frame = tk.Frame(principal)
        pesquisa_frame.pack(fill="x", pady=5)

        tk.Label(
            pesquisa_frame,
            text="Pesquisar produto:",
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=5)

        self.entrada_pesquisa = ttk.Entry(pesquisa_frame, width=35)
        self.entrada_pesquisa.pack(side="left", padx=5)
        self.entrada_pesquisa.bind(
            "<KeyRelease>", lambda evento: self.actualizar_tabela()
        )

        ttk.Button(
            pesquisa_frame,
            text="Mostrar todos",
            command=self.mostrar_todos
        ).pack(side="left", padx=5)

        # Tabela
        tabela_frame = tk.LabelFrame(
            principal,
            text="Inventário de produtos",
            font=("Arial", 11, "bold"),
            padx=5,
            pady=5
        )
        tabela_frame.pack(fill="both", expand=True, pady=8)

        colunas = (
            "codigo", "nome", "categoria",
            "preco", "quantidade", "limite"
        )

        self.tabela = ttk.Treeview(
            tabela_frame,
            columns=colunas,
            show="headings",
            height=12
        )

        titulos = {
            "codigo": "Código",
            "nome": "Nome",
            "categoria": "Categoria",
            "preco": "Preço (MT)",
            "quantidade": "Quantidade",
            "limite": "Stock mínimo"
        }

        larguras = {
            "codigo": 90,
            "nome": 190,
            "categoria": 140,
            "preco": 110,
            "quantidade": 110,
            "limite": 110
        }

        for coluna in colunas:
            self.tabela.heading(coluna, text=titulos[coluna])
            self.tabela.column(
                coluna, width=larguras[coluna], anchor="center"
            )

        barra = ttk.Scrollbar(
            tabela_frame,
            orient="vertical",
            command=self.tabela.yview
        )
        self.tabela.configure(yscrollcommand=barra.set)

        self.tabela.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        self.tabela.bind(
            "<<TreeviewSelect>>", self.seleccionar_produto
        )

        # Operações
        operacoes = tk.LabelFrame(
            principal,
            text="Operações",
            font=("Arial", 11, "bold"),
            padx=8,
            pady=8
        )
        operacoes.pack(fill="x", pady=5)

        ttk.Button(
            operacoes,
            text="Registar venda",
            command=self.vender
        ).pack(side="left", padx=5)

        ttk.Button(
            operacoes,
            text="Stock baixo",
            command=self.mostrar_stock_baixo
        ).pack(side="left", padx=5)

        ttk.Button(
            operacoes,
            text="Resumo de vendas",
            command=self.mostrar_resumo
        ).pack(side="left", padx=5)

        ttk.Button(
            operacoes,
            text="Actualizar tabela",
            command=self.actualizar_tabela
        ).pack(side="left", padx=5)

        # Estado
        self.estado = tk.Label(
            self.janela,
            text="Sistema pronto.",
            bg="#E8EDF3",
            anchor="w",
            padx=10
        )
        self.estado.pack(fill="x", side="bottom")

    def criar_campo(self, pai, texto, linha, coluna):
        tk.Label(
            pai, text=texto, font=("Arial", 10)
        ).grid(row=linha, column=coluna, padx=5, pady=7, sticky="w")

        entrada = ttk.Entry(pai, width=25)
        entrada.grid(
            row=linha, column=coluna + 1,
            padx=5, pady=7, sticky="w"
        )

        return entrada

    def obter_dados_formulario(self):
        nome = self.entrada_nome.get().strip()
        categoria = self.entrada_categoria.get().strip()

        if not nome or not categoria:
            raise ValueError("Preencha o nome e a categoria.")

        try:
            preco = float(self.entrada_preco.get())
            quantidade = int(self.entrada_quantidade.get())
            limite = int(self.entrada_limite.get())
        except ValueError:
            raise ValueError("Introduza valores numéricos válidos.")

        if preco < 0 or quantidade < 0 or limite < 0:
            raise ValueError("Os valores não podem ser negativos.")

        return nome, categoria, preco, quantidade, limite

    def registar(self):
        try:
            dados = self.obter_dados_formulario()
            codigo = self.sistema.registar_produto(*dados)

            self.actualizar_tabela()
            self.limpar_campos()

            messagebox.showinfo(
                "Sucesso",
                f"Produto registado com sucesso!\nCódigo: {codigo}"
            )
            self.estado.config(text="Produto registado.")

        except (ValueError, OSError) as erro:
            messagebox.showerror("Erro", str(erro))

    def actualizar(self):
        if not self.codigo_seleccionado:
            messagebox.showwarning(
                "Atenção", "Seleccione um produto na tabela."
            )
            return

        try:
            dados = self.obter_dados_formulario()

            sucesso = self.sistema.actualizar_produto(
                self.codigo_seleccionado, *dados
            )

            if sucesso:
                self.actualizar_tabela()
                self.limpar_campos()
                messagebox.showinfo(
                    "Sucesso", "Produto actualizado com sucesso."
                )

        except (ValueError, OSError) as erro:
            messagebox.showerror("Erro", str(erro))

    def seleccionar_produto(self, evento=None):
        seleccionado = self.tabela.selection()

        if not seleccionado:
            return

        valores = self.tabela.item(seleccionado[0], "values")

        self.codigo_seleccionado = valores[0]

        self.limpar_campos()

        self.entrada_nome.insert(0, valores[1])
        self.entrada_categoria.insert(0, valores[2])
        self.entrada_preco.insert(0, valores[3])
        self.entrada_quantidade.insert(0, valores[4])
        self.entrada_limite.insert(0, valores[5])

        self.estado.config(
            text=f"Produto seleccionado: {self.codigo_seleccionado}"
        )

    def limpar_campos(self):
        for entrada in [
            self.entrada_nome,
            self.entrada_categoria,
            self.entrada_preco,
            self.entrada_quantidade,
            self.entrada_limite
        ]:
            entrada.delete(0, tk.END)

        self.codigo_seleccionado = None
        self.tabela.selection_remove(self.tabela.selection())

    def actualizar_tabela(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        produtos = self.sistema.listar_produtos()
        termo = self.entrada_pesquisa.get().strip().lower()

        for p in produtos:
            if (
                termo
                and termo not in p["nome"].lower()
                and termo not in p["codigo"].lower()
                and termo not in p["categoria"].lower()
            ):
                continue

            self.tabela.insert(
                "",
                tk.END,
                values=(
                    p["codigo"],
                    p["nome"],
                    p["categoria"],
                    f"{p['preco']:.2f}",
                    p["quantidade"],
                    p["limite_stock"]
                )
            )

        self.estado.config(text=f"Total de produtos: {len(produtos)}")

    def mostrar_todos(self):
        self.entrada_pesquisa.delete(0, tk.END)
        self.actualizar_tabela()

    def vender(self):
        seleccionado = self.tabela.selection()

        if not seleccionado:
            messagebox.showwarning(
                "Atenção", "Seleccione um produto na tabela."
            )
            return

        valores = self.tabela.item(seleccionado[0], "values")
        codigo = valores[0]

        quantidade = simpledialog.askinteger(
            "Registar venda",
            f"Quantas unidades de {valores[1]} pretende vender?",
            minvalue=1,
            parent=self.janela
        )

        if quantidade is None:
            return

        try:
            venda = self.sistema.registar_venda(codigo, quantidade)

            self.actualizar_tabela()

            messagebox.showinfo(
                "Venda registada",
                f"Produto: {venda['nome_produto']}\n"
                f"Quantidade: {venda['quantidade']}\n"
                f"Total: {venda['total']:.2f} MT"
            )

        except (ValueError, OSError) as erro:
            messagebox.showerror("Erro na venda", str(erro))

    def mostrar_stock_baixo(self):
        try:
            produtos = self.sistema.produtos_stock_baixo()

            if not produtos:
                messagebox.showinfo(
                    "Stock baixo",
                    "Não existem produtos com stock baixo."
                )
                return

            mensagem = "PRODUTOS COM STOCK BAIXO\n\n"

            for p in produtos:
                mensagem += (
                    f"Código: {p['codigo']}\n"
                    f"Produto: {p['nome']}\n"
                    f"Quantidade: {p['quantidade']}\n"
                    f"Limite mínimo: {p['limite_stock']}\n"
                    "--------------------------\n"
                )

            messagebox.showwarning("Aviso de stock", mensagem)

        except (ValueError, OSError) as erro:
            messagebox.showerror("Erro", str(erro))

    def mostrar_resumo(self):
        try:
            resumo = self.sistema.resumo_vendas()

            mensagem = (
                "RESUMO DE VENDAS\n\n"
                f"Número de vendas: {resumo['numero_vendas']}\n"
                f"Unidades vendidas: {resumo['unidades']}\n"
                f"Valor total: {resumo['total']:.2f} MT\n\n"
                "HISTÓRICO:\n"
            )

            for venda in resumo["vendas"]:
                mensagem += (
                    f"{venda['data']} - {venda['nome_produto']} - "
                    f"{venda['quantidade']} unidade(s) - "
                    f"{venda['total']:.2f} MT\n"
                )

            if not resumo["vendas"]:
                mensagem += "Ainda não existem vendas registadas."

            janela_resumo = tk.Toplevel(self.janela)
            janela_resumo.title("Resumo de vendas")
            janela_resumo.geometry("600x450")

            texto = tk.Text(
                janela_resumo,
                wrap="word",
                font=("Arial", 10),
                padx=10,
                pady=10
            )
            texto.pack(fill="both", expand=True)

            texto.insert("1.0", mensagem)
            texto.config(state="disabled")

        except (ValueError, OSError) as erro:
            messagebox.showerror("Erro", str(erro))


if __name__ == "__main__":
    janela = tk.Tk()
    aplicacao = AplicacaoStock(janela)
    janela.mainloop()