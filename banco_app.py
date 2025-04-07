import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import traceback
from banco import Banco
from pessoa import Usuario
from conta import ContaCorrente, ContaPoupanca
from transacao import Deposito, Saque, Transferencia
from datetime import datetime
import os

class BankAppTkinter:
    def __init__(self, root):
        self.root = root
        self.banco = Banco()
        self.current_account = None
        
        # Adiciona este handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.setup_ui()
            
    def setup_theme(self):
        """Configura o tema visual da aplicação"""
        # Usa o tema padrão do sistema
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Treeview', font=('Arial', 10), rowheight=25)
    def setup_ui(self):
        """Configura a interface principal"""
        self.root.title("UFS BANK")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Barra de status
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Menu principal
        self.setup_menu()
        
        # Abas principais
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba Dashboard
        self.setup_dashboard_tab()
        
        # Aba Clientes
        self.setup_clients_tab()
        
        # Aba Contas
        self.setup_accounts_tab()
        
        # Inicializa dados de exemplo
        self.inicializar_dados_exemplo()
        self.update_clientes_table()
        self.update_contas_table()
    
    def setup_menu(self):
        """Configura o menu principal"""
        menubar = tk.Menu(self.root)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Menu Clientes
        client_menu = tk.Menu(menubar, tearoff=0)
        client_menu.add_command(label="Cadastrar", command=self.show_cadastro_cliente)
        client_menu.add_command(label="Listar", command=self.update_clientes_table)
        client_menu.add_command(label="Buscar", command=self.show_busca_cliente)
        menubar.add_cascade(label="Clientes", menu=client_menu)
        
        # Menu Contas
        account_menu = tk.Menu(menubar, tearoff=0)
        account_menu.add_command(label="Abrir Conta Corrente", command=lambda: self.show_conta_window("CORRENTE"))
        account_menu.add_command(label="Abrir Conta Poupança", command=lambda: self.show_conta_window("POUPANCA"))
        account_menu.add_command(label="Operações", command=self.show_login_window)
        account_menu.add_command(label="Relatórios", command=self.show_reports_window)
        menubar.add_cascade(label="Contas", menu=account_menu)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.show_about)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def setup_dashboard_tab(self):
        """Configura a aba Dashboard"""
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Cabeçalho
        header_frame = ttk.Frame(self.dashboard_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Bem-vindo ao Sistema Bancário", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        # Cards de resumo
        cards_frame = ttk.Frame(self.dashboard_frame)
        cards_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.total_clientes_var = tk.StringVar(value="0")
        self.total_contas_var = tk.StringVar(value="0")
        self.total_saldo_var = tk.StringVar(value="R$ 0,00")
        
        self.create_card(cards_frame, "Clientes", self.total_clientes_var)
        self.create_card(cards_frame, "Contas", self.total_contas_var)
        self.create_card(cards_frame, "Saldo Total", self.total_saldo_var)
        
        # Tabela de movimentações recentes
        ttk.Label(self.dashboard_frame, text="Últimas Movimentações", font=('Arial', 12)).pack(pady=(10, 0))
        
        self.dashboard_tree = ttk.Treeview(self.dashboard_frame, 
                                         columns=("data", "conta", "operacao", "valor", "saldo"), 
                                         show="headings")
        
        self.dashboard_tree.heading("data", text="Data/Hora")
        self.dashboard_tree.heading("conta", text="Conta")
        self.dashboard_tree.heading("operacao", text="Operação")
        self.dashboard_tree.heading("valor", text="Valor (R$)")
        self.dashboard_tree.heading("saldo", text="Saldo (R$)")
        
        for col in ("data", "conta", "operacao", "valor", "saldo"):
            self.dashboard_tree.column(col, width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(self.dashboard_frame, orient="vertical", command=self.dashboard_tree.yview)
        self.dashboard_tree.configure(yscrollcommand=scrollbar.set)
        
        self.dashboard_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Atualiza os cards
        self.update_dashboard_cards()
    
    def create_card(self, parent, title, value_var):
        """Cria um card de resumo para o dashboard"""
        card = ttk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        ttk.Label(card, text=title, font=('Arial', 10, 'bold')).pack(pady=(5, 0))
        ttk.Label(card, textvariable=value_var, font=('Arial', 14)).pack(pady=5)
    
    def setup_clients_tab(self):
        """Configura a aba de Clientes"""
        self.clientes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.clientes_frame, text="Clientes")
        
        # Barra de ferramentas
        toolbar = ttk.Frame(self.clientes_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Novo Cliente", command=self.show_cadastro_cliente).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Editar", command=self.editar_cliente).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Excluir", command=self.excluir_cliente).pack(side=tk.LEFT, padx=2)
        
        # Barra de busca
        search_frame = ttk.Frame(self.clientes_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        self.client_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.client_search_var)
        search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self.filter_clients())
        
        # Tabela de clientes
        self.clientes_tree = ttk.Treeview(self.clientes_frame, 
                                        columns=("cpf", "nome", "idade", "endereco", "contas"), 
                                        show="headings")
        
        self.clientes_tree.heading("cpf", text="CPF", command=lambda: self.sort_treeview(self.clientes_tree, "cpf", False))
        self.clientes_tree.heading("nome", text="Nome", command=lambda: self.sort_treeview(self.clientes_tree, "nome", False))
        self.clientes_tree.heading("idade", text="Idade", command=lambda: self.sort_treeview(self.clientes_tree, "idade", False))
        self.clientes_tree.heading("endereco", text="Endereço")
        self.clientes_tree.heading("contas", text="Contas")
        
        self.clientes_tree.column("cpf", width=120)
        self.clientes_tree.column("nome", width=200)
        self.clientes_tree.column("idade", width=60, anchor=tk.CENTER)
        self.clientes_tree.column("endereco", width=250)
        self.clientes_tree.column("contas", width=80, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(self.clientes_frame, orient="vertical", command=self.clientes_tree.yview)
        self.clientes_tree.configure(yscrollcommand=scrollbar.set)
        
        self.clientes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configura duplo clique para editar
        self.clientes_tree.bind('<Double-1>', lambda e: self.editar_cliente())
    
    def setup_accounts_tab(self):
        """Configura a aba de Contas"""
        self.contas_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.contas_frame, text="Contas")
        
        # Barra de ferramentas
        toolbar = ttk.Frame(self.contas_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Nova Conta Corrente", command=lambda: self.show_conta_window("CORRENTE")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Nova Poupança", command=lambda: self.show_conta_window("POUPANCA")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Acessar", command=self.show_login_window).pack(side=tk.LEFT, padx=2)
        
        # Tabela de contas
        self.contas_tree = ttk.Treeview(self.contas_frame, 
                                      columns=("numero", "tipo", "titular", "cpf", "saldo"), 
                                      show="headings")
        
        self.contas_tree.heading("numero", text="Número", command=lambda: self.sort_treeview(self.contas_tree, "numero", False))
        self.contas_tree.heading("tipo", text="Tipo", command=lambda: self.sort_treeview(self.contas_tree, "tipo", False))
        self.contas_tree.heading("titular", text="Titular", command=lambda: self.sort_treeview(self.contas_tree, "titular", False))
        self.contas_tree.heading("cpf", text="CPF")
        self.contas_tree.heading("saldo", text="Saldo (R$)", command=lambda: self.sort_treeview(self.contas_tree, "saldo", False))
        
        self.contas_tree.column("numero", width=80, anchor=tk.CENTER)
        self.contas_tree.column("tipo", width=100)
        self.contas_tree.column("titular", width=200)
        self.contas_tree.column("cpf", width=120)
        self.contas_tree.column("saldo", width=100, anchor=tk.E)
        
        scrollbar = ttk.Scrollbar(self.contas_frame, orient="vertical", command=self.contas_tree.yview)
        self.contas_tree.configure(yscrollcommand=scrollbar.set)
        
        self.contas_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configura duplo clique para acessar
        self.contas_tree.bind('<Double-1>', lambda e: self.acessar_conta_selecionada())
    
    def sort_treeview(self, tree, col, reverse):
        """Ordena a treeview pela coluna clicada"""
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        
        # Tenta converter para número se possível
        try:
            data.sort(key=lambda x: float(x[0]) if x[0].replace('.', '').isdigit() else x[0], reverse=reverse)
        except:
            data.sort(reverse=reverse)
        
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)
        
        # Inverte a ordem para a próxima vez
        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))
    
    def update_dashboard_cards(self):
        """Atualiza os cards de resumo no dashboard"""
        total_clientes = len(self.banco.get_usuarios())
        total_contas = len(self.banco.get_contas())
        total_saldo = sum(conta.get_saldo() for conta in self.banco.get_contas())
        
        self.total_clientes_var.set(str(total_clientes))
        self.total_contas_var.set(str(total_contas))
        self.total_saldo_var.set(f"R$ {total_saldo:,.2f}")
    
    def inicializar_dados_exemplo(self):
        """Inicializa dados de exemplo se não existirem"""
        if not self.banco.get_usuarios():
            try:
                usuario1 = self.banco.criar_usuario("João Silva", "12345678901", "01/01/1980", "Rua Exemplo, 123 - Centro - São Paulo/SP")
                usuario2 = self.banco.criar_usuario("Maria Souza", "98765432109", "15/05/1990", "Av. Teste, 456 - Jardim - Rio de Janeiro/RJ")
                
                conta1 = self.banco.criar_conta_corrente("12345678901", "1234")
                conta2 = self.banco.criar_conta_poupanca("98765432109", "4321")
                
                if conta1 and conta2:
                    conta1.realizar_transacao(Deposito(1000.00))
                    conta1.realizar_transacao(Saque(200.00))
                    conta2.realizar_transacao(Deposito(500.00))
                    conta1.realizar_transacao(Transferencia(300.00, conta2))
                
                self.status_var.set("Dados de exemplo criados com sucesso!")
            except Exception as e:
                self.status_var.set(f"Erro ao criar dados de exemplo: {str(e)}")
    
    # Métodos para clientes
    def show_cadastro_cliente(self, cliente=None):
        """Mostra a janela de cadastro/edição de cliente"""
        self.cadastro_window = tk.Toplevel(self.root)
        self.cadastro_window.title("Cadastrar Cliente" if not cliente else "Editar Cliente")
        self.cadastro_window.geometry("500x400")
        self.cadastro_window.transient(self.root)
        self.cadastro_window.grab_set()
        
        # Variáveis do formulário
        self.cliente_nome_var = tk.StringVar(value=cliente.get_nome() if cliente else "")
        self.cliente_cpf_var = tk.StringVar(value=cliente.get_cpf() if cliente else "")
        self.cliente_nascimento_var = tk.StringVar(value=cliente.get_data_nascimento() if cliente else "")
        self.cliente_endereco_var = tk.StringVar(value=cliente.get_endereco() if cliente else "")
        
        # Formulário
        form_frame = ttk.Frame(self.cadastro_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Nome completo:").grid(row=0, column=0, sticky=tk.W, pady=(5, 0))
        nome_entry = ttk.Entry(form_frame, textvariable=self.cliente_nome_var)
        nome_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 5))
        
        ttk.Label(form_frame, text="CPF (apenas números):").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        cpf_entry = ttk.Entry(form_frame, textvariable=self.cliente_cpf_var, state='disabled' if cliente else 'normal')
        cpf_entry.grid(row=3, column=0, sticky=tk.EW, pady=(0, 5))
        
        ttk.Label(form_frame, text="Data Nascimento (DD/MM/AAAA):").grid(row=4, column=0, sticky=tk.W, pady=(5, 0))
        nascimento_entry = ttk.Entry(form_frame, textvariable=self.cliente_nascimento_var)
        nascimento_entry.grid(row=5, column=0, sticky=tk.EW, pady=(0, 5))
        
        ttk.Label(form_frame, text="Endereço:").grid(row=6, column=0, sticky=tk.W, pady=(5, 0))
        endereco_entry = ttk.Entry(form_frame, textvariable=self.cliente_endereco_var)
        endereco_entry.grid(row=7, column=0, sticky=tk.EW, pady=(0, 10))
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=8, column=0, sticky=tk.EW, pady=10)
        
        ttk.Button(btn_frame, text="Salvar", 
                  command=lambda: self.salvar_cliente(cliente)).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=self.cadastro_window.destroy).pack(side=tk.LEFT, expand=True, padx=5)
        
        # Configura expansão
        form_frame.columnconfigure(0, weight=1)
        
        # Focar no primeiro campo
        nome_entry.focus_set()
    
    def salvar_cliente(self, cliente=None):
        """Salva um novo cliente ou atualiza um existente"""
        try:
            nome = self.cliente_nome_var.get()
            cpf = self.cliente_cpf_var.get()
            data_nasc = self.cliente_nascimento_var.get()
            endereco = self.cliente_endereco_var.get()
            
            if not all([nome, cpf, data_nasc, endereco]):
                raise ValueError("Todos os campos são obrigatórios")
            
            if cliente:
                # Atualiza cliente existente
                cliente.set_nome(nome)
                cliente.set_data_nascimento(data_nasc)
                cliente.set_endereco(endereco)
                self.status_var.set("Cliente atualizado com sucesso!")
            else:
                # Cria novo cliente
                self.banco.criar_usuario(nome, cpf, data_nasc, endereco)
                self.status_var.set("Cliente cadastrado com sucesso!")
            
            self.cadastro_window.destroy()
            self.update_clientes_table()
            self.update_dashboard_cards()
        except ValueError as e:
            messagebox.showerror("Erro", str(e), parent=self.cadastro_window)
    
    def update_clientes_table(self):
        """Atualiza a tabela de clientes"""
        for row in self.clientes_tree.get_children():
            self.clientes_tree.delete(row)
            
        for usuario in self.banco.get_usuarios():
            self.clientes_tree.insert("", tk.END, values=(
                usuario.get_cpf(),
                usuario.get_nome(),
                usuario.get_idade(),
                usuario.get_endereco(),
                len(usuario.get_contas())
            ))
    
    def filter_clients(self):
        """Filtra clientes na tabela conforme texto digitado"""
        search_term = self.client_search_var.get().lower()
        
        for child in self.clientes_tree.get_children():
            values = self.clientes_tree.item(child)['values']
            if (search_term in values[0].lower() or  # CPF
                search_term in values[1].lower() or  # Nome
                search_term in values[3].lower()):   # Endereço
                self.clientes_tree.item(child, tags=('match',))
                self.clientes_tree.tag_configure('match', background='yellow')
            else:
                self.clientes_tree.item(child, tags=('no_match',))
                self.clientes_tree.tag_configure('no_match', background='')
    
    def show_busca_cliente(self):
        """Mostra diálogo de busca de cliente"""
        cpf = simpledialog.askstring("Buscar Cliente", "Digite o CPF:", parent=self.root)
        if cpf:
            usuario = self.banco._buscar_usuario(cpf)
            if usuario:
                messagebox.showinfo("Cliente Encontrado", 
                                  f"Nome: {usuario.get_nome()}\n"
                                  f"CPF: {usuario.get_cpf()}\n"
                                  f"Idade: {usuario.get_idade()}\n"
                                  f"Contas: {len(usuario.get_contas())}",
                                  parent=self.root)
            else:
                messagebox.showerror("Erro", "Cliente não encontrado", parent=self.root)
    
    def editar_cliente(self):
        """Edita o cliente selecionado"""
        selected = self.clientes_tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar", parent=self.root)
            return
        
        values = self.clientes_tree.item(selected)['values']
        cpf = values[0]
        
        usuario = self.banco._buscar_usuario(cpf)
        if usuario:
            self.show_cadastro_cliente(usuario)
    
    def excluir_cliente(self):
        """Exclui o cliente selecionado"""
        selected = self.clientes_tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir", parent=self.root)
            return
        
        values = self.clientes_tree.item(selected)['values']
        cpf = values[0]
        
        if messagebox.askyesno("Confirmar", f"Excluir cliente {values[1]}?", parent=self.root):
            try:
                # Remove todas as contas do cliente primeiro
                usuario = self.banco._buscar_usuario(cpf)
                if usuario:
                    for conta in usuario.get_contas():
                        self.banco._contas.remove(conta)
                
                # Remove o usuário
                self.banco._usuarios.remove(usuario)
                self.banco._salvar_dados()
                
                self.update_clientes_table()
                self.update_contas_table()
                self.update_dashboard_cards()
                self.status_var.set("Cliente excluído com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir cliente: {str(e)}", parent=self.root)
    
    # Métodos para contas
    def show_conta_window(self, tipo):
        """Mostra a janela para criar nova conta"""
        self.conta_window = tk.Toplevel(self.root)
        self.conta_window.title(f"Abrir Conta {tipo}")
        self.conta_window.geometry("400x200")
        self.conta_window.transient(self.root)
        self.conta_window.grab_set()
        
        # Formulário
        form_frame = ttk.Frame(self.conta_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(form_frame, text="CPF do titular:").grid(row=0, column=0, sticky=tk.W, pady=(5, 0))
        self.conta_cpf_var = tk.StringVar()
        cpf_entry = ttk.Entry(form_frame, textvariable=self.conta_cpf_var)
        cpf_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 5))
        
        ttk.Label(form_frame, text="Senha (4 dígitos):").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.conta_senha_var = tk.StringVar()
        senha_entry = ttk.Entry(form_frame, textvariable=self.conta_senha_var, show="*")
        senha_entry.grid(row=3, column=0, sticky=tk.EW, pady=(0, 10))
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, sticky=tk.EW, pady=10)
        
        if tipo == "CORRENTE":
            ttk.Button(btn_frame, text="Criar Conta Corrente", 
                      command=lambda: self.criar_conta("CORRENTE")).pack(side=tk.LEFT, expand=True, padx=5)
        else:
            ttk.Button(btn_frame, text="Criar Conta Poupança", 
                      command=lambda: self.criar_conta("POUPANCA")).pack(side=tk.LEFT, expand=True, padx=5)
            
        ttk.Button(btn_frame, text="Cancelar", 
                  command=self.conta_window.destroy).pack(side=tk.LEFT, expand=True, padx=5)
        
        # Configura expansão
        form_frame.columnconfigure(0, weight=1)
        
        # Focar no campo CPF
        cpf_entry.focus_set()
    
    def criar_conta(self, tipo):
        """Cria uma nova conta do tipo especificado"""
        try:
            cpf = self.conta_cpf_var.get()
            senha = self.conta_senha_var.get()
            
            if not cpf or not senha:
                raise ValueError("Todos os campos são obrigatórios")
                
            # Remove formatação do CPF para busca interna
            cpf_limpo = cpf.replace(".", "").replace("-", "")
            
            if tipo == "CORRENTE":
                conta = self.banco.criar_conta_corrente(cpf_limpo, senha)
                msg = "Conta corrente criada com sucesso!"
            else:
                conta = self.banco.criar_conta_poupanca(cpf_limpo, senha)
                msg = "Conta poupança criada com sucesso!"
            
            self.conta_window.destroy()
            self.update_contas_table()
            self.update_dashboard_cards()
            self.status_var.set(msg)
        except ValueError as e:
            messagebox.showerror("Erro", str(e), parent=self.conta_window)
    
    def update_contas_table(self):
        """Atualiza a tabela de contas"""
        for row in self.contas_tree.get_children():
            self.contas_tree.delete(row)
        
        for conta in self.banco.get_contas():
            cliente = conta.get_cliente()
            self.contas_tree.insert("", tk.END, values=(
                conta.get_numero(),
                "Corrente" if isinstance(conta, ContaCorrente) else "Poupança",
                cliente.get_nome(),
                cliente.get_cpf(),
                f"{conta.get_saldo():,.2f}"
            ))
    
    def acessar_conta_selecionada(self):
        """Acessa a conta selecionada na tabela"""
        selected = self.contas_tree.focus()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma conta para acessar", parent=self.root)
            return
        
        values = self.contas_tree.item(selected)['values']
        numero_conta = values[0]
        cpf = values[3]
        
        # Pede a senha
        senha = simpledialog.askstring("Acesso à Conta", 
                                      f"Digite a senha para a conta {numero_conta}:", 
                                      parent=self.root, show="*")
        if senha:
            conta = self.banco.acessar_conta(cpf, "0001", numero_conta, senha)
            if conta:
                self.current_account = conta
                self.show_menu_operacoes()
            else:
                messagebox.showerror("Erro", "Senha incorreta", parent=self.root)
    
    def show_login_window(self):
        """Mostra a janela de login para acessar uma conta"""
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Acessar Conta")
        self.login_window.geometry("400x250")
        self.login_window.transient(self.root)
        self.login_window.grab_set()
        
        # Formulário
        form_frame = ttk.Frame(self.login_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(form_frame, text="CPF (com ou sem formatação):").grid(row=0, column=0, sticky=tk.W, pady=(5, 0))
        self.login_cpf_var = tk.StringVar()
        cpf_entry = ttk.Entry(form_frame, textvariable=self.login_cpf_var)
        cpf_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 5))
        
        ttk.Label(form_frame, text="Número da Conta:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.login_numero_var = tk.StringVar()
        numero_entry = ttk.Entry(form_frame, textvariable=self.login_numero_var)
        numero_entry.grid(row=3, column=0, sticky=tk.EW, pady=(0, 5))
        
        ttk.Label(form_frame, text="Senha (4 dígitos):").grid(row=4, column=0, sticky=tk.W, pady=(5, 0))
        self.login_senha_var = tk.StringVar()
        senha_entry = ttk.Entry(form_frame, textvariable=self.login_senha_var, show="*")
        senha_entry.grid(row=5, column=0, sticky=tk.EW, pady=(0, 10))
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, sticky=tk.EW, pady=10)
        
        ttk.Button(btn_frame, text="Acessar", 
                command=self.realizar_login).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                command=self.login_window.destroy).pack(side=tk.LEFT, expand=True, padx=5)
        
        # Configura expansão
        form_frame.columnconfigure(0, weight=1)
        
        # Focar no campo CPF
        cpf_entry.focus_set()
    
    def realizar_login(self):
        try:
            cpf = self.login_cpf_var.get().strip()
            numero_conta = self.login_numero_var.get().strip()
            senha = self.login_senha_var.get().strip()
            
            print(f"Tentativa de login - CPF: {cpf}, Conta: {numero_conta}")  # Log
            
            if not all([cpf, numero_conta, senha]):
                raise ValueError("Todos os campos são obrigatórios")
                
            try:
                numero_conta = int(numero_conta)
            except ValueError:
                raise ValueError("Número da conta deve ser um valor inteiro")
            
            conta = self.banco.acessar_conta(cpf, "0001", numero_conta, senha)
            if conta:
                self.current_account = conta
                self.login_window.destroy()
                self.show_menu_operacoes()
            else:
                raise ValueError("CPF, número da conta ou senha incorretos")
                
        except ValueError as e:
            print(f"Erro no login: {str(e)}")  # Log
            messagebox.showerror("Erro", str(e), parent=self.login_window)
        
    def show_menu_operacoes(self):
        """Mostra o menu de operações para a conta logada"""
        if not self.current_account:
            return
            
        self.operacoes_window = tk.Toplevel(self.root)
        self.operacoes_window.title("Operações Bancárias")
        self.operacoes_window.geometry("600x500")
        self.operacoes_window.transient(self.root)
        self.operacoes_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self.operacoes_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Informações da conta
        info_frame = ttk.LabelFrame(main_frame, text="Informações da Conta", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, 
                 text=f"Conta: {self.current_account.get_numero()} - {'Corrente' if isinstance(self.current_account, ContaCorrente) else 'Poupança'}", 
                 font=('Arial', 12)).pack(anchor=tk.W)
        
        ttk.Label(info_frame, 
                 text=f"Titular: {self.current_account.get_cliente().get_nome()}", 
                 font=('Arial', 10)).pack(anchor=tk.W)
        
        ttk.Label(info_frame, 
                 text=f"Saldo: R$ {self.current_account.get_saldo():,.2f}", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Botões de operações
        btn_frame = ttk.LabelFrame(main_frame, text="Operações", padding=10)
        btn_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configuração dos botões
        buttons = [
            ("Depósito", self.show_deposito_window),
            ("Saque", self.show_saque_window),
            ("Transferência", self.show_transferencia_window),
            ("Extrato", self.mostrar_extrato),
            ("Histórico Completo", self.mostrar_historico_completo)
        ]
        
        if isinstance(self.current_account, ContaPoupanca):
            buttons.append(("Calcular Rendimento", self.calcular_rendimento))
        
        for text, command in buttons:
            ttk.Button(btn_frame, text=text, command=command).pack(fill=tk.X, pady=5)
        
        # Botão de fechar
        ttk.Button(main_frame, text="Fechar", 
                  command=self.operacoes_window.destroy).pack(pady=10)
    
    def show_deposito_window(self):
        """Mostra a janela de depósito"""
        self.deposito_window = tk.Toplevel(self.operacoes_window)
        self.deposito_window.title("Depósito")
        self.deposito_window.geometry("300x150")
        self.deposito_window.transient(self.operacoes_window)
        self.deposito_window.grab_set()
        
        # Formulário
        form_frame = ttk.Frame(self.deposito_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Valor (R$):").pack(pady=(5, 0))
        self.deposito_valor_var = tk.StringVar()
        valor_entry = ttk.Entry(form_frame, textvariable=self.deposito_valor_var)
        valor_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Confirmar", 
                  command=self.realizar_deposito).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=self.deposito_window.destroy).pack(side=tk.LEFT, expand=True, padx=5)
        
        # Focar no campo de valor
        valor_entry.focus_set()
    
    def realizar_deposito(self):
        """Realiza um depósito na conta"""
        try:
            valor_str = self.deposito_valor_var.get().replace(",", ".")
            valor = float(valor_str)
            
            if valor <= 0:
                raise ValueError("O valor deve ser positivo")
                
            transacao = Deposito(valor)
            if self.current_account.realizar_transacao(transacao):
                self.deposito_window.destroy()
                self.update_contas_table()
                self.status_var.set(f"Depósito de R$ {valor:.2f} realizado com sucesso!")
                self.operacoes_window.destroy()
                self.show_menu_operacoes()
                
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}", parent=self.deposito_window)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no depósito: {str(e)}", parent=self.deposito_window)
            print(f"Erro detalhado: {traceback.format_exc()}")
    
    def show_saque_window(self):
        """Mostra a janela de saque"""
        self.saque_window = tk.Toplevel(self.operacoes_window)
        self.saque_window.title("Saque")
        self.saque_window.geometry("300x150")
        self.saque_window.transient(self.operacoes_window)
        self.saque_window.grab_set()
        
        # Formulário
        form_frame = ttk.Frame(self.saque_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Valor (R$):").pack(pady=(5, 0))
        self.saque_valor_var = tk.StringVar()
        valor_entry = ttk.Entry(form_frame, textvariable=self.saque_valor_var)
        valor_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Limite de saque
        if isinstance(self.current_account, ContaCorrente):
            saldo_disponivel = self.current_account.get_saldo() + self.current_account.get_limite()
            ttk.Label(form_frame, 
                      text=f"Saldo disponível: R$ {saldo_disponivel:,.2f}").pack()
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Confirmar", 
                  command=self.realizar_saque).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=self.saque_window.destroy).pack(side=tk.LEFT, expand=True, padx=5)
        
        # Focar no campo de valor
        valor_entry.focus_set()
    
    def realizar_saque(self):
        """Realiza um saque na conta"""
        try:
            valor_str = self.saque_valor_var.get().replace(",", ".")
            valor = float(valor_str)
            
            if valor <= 0:
                raise ValueError("O valor deve ser positivo")
                
            transacao = Saque(valor)
            if self.current_account.realizar_transacao(transacao):
                self.saque_window.destroy()
                self.update_contas_table()
                self.status_var.set(f"Saque de R$ {valor:.2f} realizado com sucesso!")
                self.operacoes_window.destroy()
                self.show_menu_operacoes()
                
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}", parent=self.saque_window)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no saque: {str(e)}", parent=self.saque_window)
            print(f"Erro detalhado: {traceback.format_exc()}")
    
    def show_transferencia_window(self):
        """Mostra a janela de transferência"""
        self.transferencia_window = tk.Toplevel(self.operacoes_window)
        self.transferencia_window.title("Transferência")
        self.transferencia_window.geometry("400x250")
        self.transferencia_window.transient(self.operacoes_window)
        self.transferencia_window.grab_set()
        
        # Formulário
        form_frame = ttk.Frame(self.transferencia_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Valor (R$):").grid(row=0, column=0, sticky=tk.W, pady=(5, 0))
        self.transferencia_valor_var = tk.StringVar()
        valor_entry = ttk.Entry(form_frame, textvariable=self.transferencia_valor_var)
        valor_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 5))
        
        ttk.Label(form_frame, text="Número da conta destino:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.transferencia_destino_var = tk.StringVar()
        destino_entry = ttk.Entry(form_frame, textvariable=self.transferencia_destino_var)
        destino_entry.grid(row=3, column=0, sticky=tk.EW, pady=(0, 10))
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, sticky=tk.EW, pady=10)
        
        ttk.Button(btn_frame, text="Confirmar", 
                  command=self.realizar_transferencia).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=self.transferencia_window.destroy).pack(side=tk.LEFT, expand=True, padx=5)
        
        # Configura expansão
        form_frame.columnconfigure(0, weight=1)
        
        # Focar no campo de valor
        valor_entry.focus_set()
    
    def realizar_transferencia(self):
        """Realiza uma transferência para outra conta"""
        try:
            valor = float(self.transferencia_valor_var.get())
            numero_destino = int(self.transferencia_destino_var.get())
            
            if valor <= 0:
                raise ValueError("O valor deve ser positivo")
                
            conta_destino = None
            for c in self.banco.get_contas():
                if c.get_numero() == numero_destino:
                    conta_destino = c
                    break
            
            if conta_destino:
                transacao = Transferencia(valor, conta_destino)
                self.current_account.realizar_transacao(transacao)
                self.transferencia_window.destroy()
                self.update_contas_table()
                self.status_var.set(f"Transferência de R$ {valor:,.2f} realizada com sucesso!")
                self.operacoes_window.destroy()
                self.show_menu_operacoes()
            else:
                raise ValueError("Conta destino não encontrada")
        except ValueError as e:
            messagebox.showerror("Erro", str(e), parent=self.transferencia_window)
    
    def mostrar_extrato(self):
        """Mostra um extrato resumido da conta"""
        extrato_window = tk.Toplevel(self.operacoes_window)
        extrato_window.title("Extrato Bancário")
        extrato_window.geometry("600x400")
        extrato_window.transient(self.operacoes_window)
        extrato_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(extrato_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, 
                 text=f"Extrato - Conta {self.current_account.get_numero()}",
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        ttk.Label(header_frame, 
                 text=f"Saldo: R$ {self.current_account.get_saldo():,.2f}",
                 font=('Arial', 12)).pack(side=tk.RIGHT)
        
        # Área de texto
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        extrato_text = tk.Text(text_frame, yscrollcommand=scrollbar.set, wrap=tk.WORD,
                              font=('Arial', 10), padx=5, pady=5)
        extrato_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=extrato_text.yview)
        
        # Obter extrato da conta
        extrato = self.current_account.gerar_extrato()
        extrato_text.insert(tk.END, extrato)
        extrato_text.config(state=tk.DISABLED)
        
        # Botão de fechar
        ttk.Button(main_frame, text="Fechar", 
                  command=extrato_window.destroy).pack(pady=10)
    
    def mostrar_historico_completo(self):
        """Mostra o histórico completo de transações"""
        historico_window = tk.Toplevel(self.operacoes_window)
        historico_window.title("Histórico Completo")
        historico_window.geometry("800x600")
        historico_window.transient(self.operacoes_window)
        historico_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(historico_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, 
                 text=f"Histórico - Conta {self.current_account.get_numero()}",
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Tabela de transações
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        historico_tree = ttk.Treeview(tree_frame, 
                                    columns=("data", "tipo", "valor", "saldo"), 
                                    show="headings")
        
        historico_tree.heading("data", text="Data/Hora")
        historico_tree.heading("tipo", text="Tipo")
        historico_tree.heading("valor", text="Valor (R$)")
        historico_tree.heading("saldo", text="Saldo (R$)")
        
        for col in ("data", "tipo", "valor", "saldo"):
            historico_tree.column(col, width=150, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=historico_tree.yview)
        historico_tree.configure(yscrollcommand=scrollbar.set)
        
        historico_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preenche a tabela com as transações
        transacoes = self.current_account.get_historico().get_transacoes()
        saldo = 0
        
        for transacao in transacoes:
            if transacao['tipo'] == 'Deposito':
                saldo += transacao['valor']
            else:
                saldo -= transacao['valor']
            
            historico_tree.insert("", tk.END, values=(
                transacao['data'],
                transacao['tipo'],
                f"{transacao['valor']:,.2f}",
                f"{saldo:,.2f}"
            ))
        
        # Botão de fechar
        ttk.Button(main_frame, text="Fechar", 
                  command=historico_window.destroy).pack(pady=10)
    
    def calcular_rendimento(self):
        """Calcula e aplica o rendimento da poupança"""
        if isinstance(self.current_account, ContaPoupanca):
            try:
                rendimento = self.current_account.calcular_rendimento()
                self.status_var.set(f"Rendimento de R$ {rendimento:,.2f} aplicado!")
                self.update_contas_table()
                self.operacoes_window.destroy()
                self.show_menu_operacoes()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao calcular rendimento: {str(e)}", 
                                    parent=self.operacoes_window)
    
    def show_reports_window(self):
        """Mostra a janela de relatórios"""
        reports_window = tk.Toplevel(self.root)
        reports_window.title("Relatórios")
        reports_window.geometry("600x400")
        reports_window.transient(self.root)
        reports_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(reports_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(main_frame, text="Relatórios Disponíveis", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Botões de relatórios
        ttk.Button(main_frame, text="Clientes por Faixa Etária", 
                  command=self.gerar_relatorio_idade).pack(fill=tk.X, pady=5)
        
        ttk.Button(main_frame, text="Saldos por Tipo de Conta", 
                  command=self.gerar_relatorio_saldos).pack(fill=tk.X, pady=5)
        
        ttk.Button(main_frame, text="Movimentações por Período", 
                  command=self.gerar_relatorio_movimentacoes).pack(fill=tk.X, pady=5)
        
        # Botão de fechar
        ttk.Button(main_frame, text="Fechar", 
                  command=reports_window.destroy).pack(pady=10)
    
    def gerar_relatorio_idade(self):
        """Gera relatório de clientes por faixa etária"""
        # Implementar lógica do relatório
        messagebox.showinfo("Relatório", "Relatório de clientes por faixa etária gerado", parent=self.root)
    
    def gerar_relatorio_saldos(self):
        """Gera relatório de saldos por tipo de conta"""
        # Implementar lógica do relatório
        messagebox.showinfo("Relatório", "Relatório de saldos por tipo de conta gerado", parent=self.root)
    
    def gerar_relatorio_movimentacoes(self):
        """Gera relatório de movimentações por período"""
        # Implementar lógica do relatório
        messagebox.showinfo("Relatório", "Relatório de movimentações por período gerado", parent=self.root)
    
    def show_about(self):
        """Mostra a janela 'Sobre'"""
        messagebox.showinfo("Sobre", 
                          "UFS BANK\n"
                          "Versão 1.0\n\n"
                          "Desenvolvido como projeto de POO\n"
                          "© 2025 - Todos os direitos reservados",
                          parent=self.root)


    def on_close(self):
        """Executado quando a janela principal é fechada"""
        try:
            self.banco._salvar_dados()  # Força salvar antes de fechar
            self.root.destroy()
        except Exception as e:
            print(f"Erro ao salvar dados: {str(e)}")
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = BankAppTkinter(root)
    root.mainloop()