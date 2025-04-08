from datetime import datetime
from conta import ContaCorrente, ContaPoupanca
from pessoa import Usuario
from utils import valida_nome, valida_data_nascimento, valida_cpf, valida_senha
from database_manager import DatabaseManager
import hashlib
import os

class Banco:
    """Classe principal que gerencia usuários e contas do banco."""
    
    def __init__(self, arquivo_json='banco_ufs.json'):
        self.db_manager = DatabaseManager(arquivo_json)
        self._usuarios = []
        self._contas = []
        self._contas_poupanca_ativas = [] 
        self._carregar_dados()
        if self._contas:
            self._ultimo_numero_conta = max(c.get_numero() for c in self._contas)
        else:
            self._ultimo_numero_conta = 0

    def _proximo_numero_conta(self):
        """Retorna o próximo número de conta sequencial"""
        self._ultimo_numero_conta += 1
        self._salvar_dados()  
        return self._ultimo_numero_conta

    def _hash_senha(self, senha):
        """Gera hash SHA-256 para a senha com salt fixo para testes"""
        salt = "OLHAAEXPLOSAODANDADAN" 
        return hashlib.sha256((salt + senha).encode()).hexdigest()

    def _carregar_dados(self):
        """Carrega dados do arquivo JSON."""
        dados = self.db_manager.load_data()
        
        self._usuarios = []
        for usuario_data in dados.get('usuarios', []):
            usuario = Usuario(
                usuario_data['nome'],
                usuario_data['cpf'],
                usuario_data['data_nascimento'],
                usuario_data['endereco']
            )
            self._usuarios.append(usuario)
        
        self._contas = []
        self._contas_poupanca_ativas = []
        for conta_data in dados.get('contas', []):
            usuario = self._buscar_usuario(conta_data['cpf_cliente'])
            if usuario:
                if conta_data['tipo'] == 'corrente':
                    conta = ContaCorrente(usuario, conta_data['numero'])
                    conta._limite = conta_data.get('limite', 500.0)  # Valor padrão
                    conta._limite_saques = conta_data.get('limite_saques', 3)  # Valor padrão
                    conta._saques_realizados = conta_data.get('saques_realizados', 0)
                    data_ultimo_saque = conta_data.get('data_ultimo_saque')
                    conta._data_ultimo_saque = datetime.strptime(data_ultimo_saque, "%Y-%m-%d").date() if data_ultimo_saque else None
                elif conta_data['tipo'] == 'poupanca':
                    conta = ContaPoupanca(usuario, conta_data['numero'])
                    conta._taxa_rendimento = conta_data.get('taxa_rendimento', 0.05)  # 5% padrão
                    data_ultimo_rendimento = conta_data.get('data_ultimo_rendimento')
                    conta._data_ultimo_rendimento = datetime.strptime(data_ultimo_rendimento, "%Y-%m-%d %H:%M:%S") if data_ultimo_rendimento else datetime.now()
                    self._contas_poupanca_ativas.append(conta)
                
                conta._saldo = conta_data.get('saldo', 0.0)
                conta.senha_hash = conta_data.get('senha_hash', '')
                self._contas.append(conta)
                usuario.add_conta(conta)
        
        self._ultimo_numero_conta = dados.get('ultimo_numero_conta', 0)

    def encerrar_contas_poupanca(self):
        """Encerra todas as threads de rendimento ao fechar o app."""
        for conta in self._contas:
            if isinstance(conta, ContaPoupanca):
                conta.encerrar()
        self._contas_poupanca_ativas = [] 

    def _salvar_dados(self):
        """Salva dados no arquivo JSON."""
        dados = {
            'usuarios': [u.to_dict() for u in self._usuarios],
            'contas': [self._conta_to_dict(c) for c in self._contas],
            'ultimo_numero_conta': self._ultimo_numero_conta
        }
        self.db_manager.save_data(dados)

    def _conta_to_dict(self, conta):
        """Converte objeto Conta para dicionário."""
        dados = conta.to_dict()
        if hasattr(conta, 'senha_hash'):
            dados['senha_hash'] = conta.senha_hash
        return dados

    def _buscar_usuario(self, cpf):
        """Busca usuário pelo CPF (com ou sem formatação)"""
        cpf_limpo = cpf.replace(".", "").replace("-", "")
        
        for usuario in self._usuarios:
            usuario_cpf_limpo = usuario.get_cpf().replace(".", "").replace("-", "")
            if usuario_cpf_limpo == cpf_limpo:
                return usuario
        return None
    

    def realizar_transacao(self, transacao):
        """Registra uma transação na conta e salva os dados"""
        try:
            if transacao.registrar(self):
                self._salvar_dados()  
                return True
            return False
        except Exception as e:
            print(f"Erro na transação: {str(e)}")
            return False

    def get_usuarios(self):
        """Retorna lista de usuários."""
        return self._usuarios
    
    def get_contas(self):
        """Retorna lista de contas."""
        return self._contas
    
    
    def criar_usuario(self, nome, cpf, data_nascimento, endereco):
        """Cria um novo usuário no sistema."""
        if not valida_nome(nome):
            raise ValueError("Nome inválido")
        if not valida_cpf(cpf):
            raise ValueError("CPF inválido")
        if not valida_data_nascimento(data_nascimento):
            raise ValueError("Data de nascimento inválida ou menor de 18 anos")
        
        if self._buscar_usuario(cpf):
            raise ValueError("Usuário com este CPF já existe")
        
        usuario = Usuario(nome, cpf, data_nascimento, endereco)
        self._usuarios.append(usuario)
        self._salvar_dados()
        return usuario
    
    def criar_conta_corrente(self, cpf, senha):
        if not valida_senha(senha, 4):
            raise ValueError("Senha deve ter 4 dígitos")
        
        usuario = self._buscar_usuario(cpf)
        if not usuario:
            raise ValueError("Usuário não encontrado")
        
        numero = self._proximo_numero_conta()
        conta = ContaCorrente(usuario, numero)
        conta.senha_hash = self._hash_senha(senha)  
        self._contas.append(conta)
        usuario.add_conta(conta)
        self._salvar_dados()
        print(f"Conta criada - Número: {numero}, CPF: {cpf}, Hash: {conta.senha_hash}")
        return conta

    def criar_conta_poupanca(self, cpf, senha):
        """Cria uma nova conta poupança."""
        if not valida_senha(senha, 4):
            raise ValueError("Senha deve ter 4 dígitos")
        
        usuario = self._buscar_usuario(cpf)
        if not usuario:
            raise ValueError("Usuário não encontrado")
        
        numero = self._proximo_numero_conta()
        conta = ContaPoupanca(usuario, numero)
        conta.senha_hash = self._hash_senha(senha)
        self._contas.append(conta)
        usuario.add_conta(conta)
        self._salvar_dados()
        return conta
            
    def acessar_conta(self, cpf, agencia, numero, senha):
        """Autentica e retorna uma conta se as credenciais estiverem corretas."""
        print(f"Tentando acessar - CPF: {cpf}, Agência: {agencia}, Número: {numero}")
        
        cpf_limpo = cpf.replace(".", "").replace("-", "")
        
        for conta in self._contas:
            conta_cpf = conta.get_cliente().get_cpf().replace(".", "").replace("-", "")
            print(f"Conta disponível - Número: {conta.get_numero()}, CPF: {conta_cpf}, Hash: {conta.senha_hash}")
            
            if conta_cpf == cpf_limpo and conta.get_numero() == numero:
                print(f"Hash da senha digitada: {self._hash_senha(senha)}")
                if conta.senha_hash == self._hash_senha(senha):
                    print("Acesso concedido!")
                    return conta
                else:
                    print("Senha incorreta!")
        
        print("Acesso negado - não encontrou correspondência")
        return None