from datetime import date, datetime
from decimal import Decimal
import traceback
from conta import ContaCorrente, ContaPoupanca
from pessoa import Usuario
from utils import valida_nome, valida_data_nascimento, valida_cpf, valida_senha
from database_manager import DatabaseManager
import hashlib
import os

class Banco:
    def __init__(self, arquivo_json='banco_ufs.json'):
        self.db_manager = DatabaseManager(arquivo_json)
        self._usuarios = []
        self._contas = []
        self._contas_poupanca_ativas = [] 
        self._carregar_dados()        
        for conta in self._contas:
            conta._banco = self
            
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
        
        # Limpa listas existentes
        self._usuarios = []
        self._contas = []
        self._contas_poupanca_ativas = []
        
        # Carrega usuários
        for usuario_data in dados.get('usuarios', []):
            try:
                usuario = Usuario(
                    usuario_data['nome'],
                    usuario_data['cpf'],
                    usuario_data['data_nascimento'],
                    usuario_data['endereco']
                )
                self._usuarios.append(usuario)
            except Exception as e:
                print(f"Erro ao carregar usuário: {str(e)}")
        
        # Carrega contas
        for conta_data in dados.get('contas', []):
            try:
                usuario = self._buscar_usuario(conta_data['cpf_cliente'])
                if not usuario:
                    print(f"Usuário não encontrado para conta {conta_data['numero']}")
                    continue
                    
                if conta_data['tipo'] == 'corrente':
                    conta = ContaCorrente(
                        usuario, 
                        conta_data['numero'],
                        limite=float(conta_data.get('limite', 500.0)),
                        limite_saques=int(conta_data.get('limite_saques', 3)))
                    
                    # Atributos específicos
                    conta._saldo = float(conta_data.get('saldo', 0.0))
                    conta._saques_realizados = int(conta_data.get('saques_realizados', 0))
                    
                    # Data do último saque
                    if conta_data.get('data_ultimo_saque'):
                        try:
                            conta._data_ultimo_saque = datetime.strptime(
                                conta_data['data_ultimo_saque'], "%Y-%m-%d").date()
                        except:
                            conta._data_ultimo_saque = None
                    
                    # Empréstimos
                    conta._emprestimos = conta_data.get('emprestimos', [])
                    
                elif conta_data['tipo'] == 'poupanca':
                    conta = ContaPoupanca(
                        usuario, 
                        conta_data['numero'],
                        taxa_rendimento=float(conta_data.get('taxa_rendimento', 0.05)))
                    
                    # Atributos específicos
                    conta._saldo = float(conta_data.get('saldo', 0.0))
                    
                    # Data do último rendimento
                    if conta_data.get('ultima_atualizacao'):
                        try:
                            conta._ultima_atualizacao = datetime.strptime(
                                conta_data['ultima_atualizacao'], "%Y-%m-%d %H:%M:%S")
                        except:
                            conta._ultima_atualizacao = datetime.now()
                    else:
                        conta._ultima_atualizacao = datetime.now()
                    
                    # Inicia thread de rendimento
                    conta._iniciar_rendimento_automatico()
                    self._contas_poupanca_ativas.append(conta)
                
                # Configurações comuns
                conta.senha_hash = conta_data.get('senha_hash', "")
                
                # Histórico
                if 'historico' in conta_data:
                    for transacao in conta_data['historico']:
                        conta.get_historico()._transacoes.append(transacao)
                
                # Vincula o banco à conta
                conta._banco = self
                self._contas.append(conta)
                
                # Adiciona conta ao usuário
                usuario.add_conta(conta)
                
            except Exception as e:
                print(f"Erro ao carregar conta {conta_data.get('numero', '?')}: {str(e)}")
                traceback.print_exc()
        
        self._ultimo_numero_conta = dados.get('ultimo_numero_conta', 0)



    def salvar_dados_imediato(self):
        """Força o salvamento imediato dos dados com tratamento de erros."""
        try:
            # Encerra temporariamente as threads de poupança
            for conta in self._contas_poupanca_ativas:
                conta._rodando = False
                if conta._thread_rendimento:
                    conta._thread_rendimento.join(timeout=1)
            
            # Realiza o salvamento
            self._salvar_dados()
            
            # Reinicia as threads
            for conta in self._contas_poupanca_ativas:
                conta._iniciar_rendimento_automatico()
                
        except Exception as e:
            print(f"ERRO CRÍTICO AO SALVAR: {str(e)}")
            traceback.print_exc()
    def encerrar_contas_poupanca(self):
        """Encerra todas as threads de rendimento ao fechar o app."""
        for conta in self._contas:
            if isinstance(conta, ContaPoupanca):
                conta.encerrar()
                # Força um último salvamento
                if hasattr(conta, '_banco'):
                    conta._banco._salvar_dados()
        self._contas_poupanca_ativas = []

    def verificar_senhas(self):
        """Verifica todas as contas por senhas ausentes"""
        sem_senha = []
        for conta in self._contas:
            if not conta.senha_hash:
                sem_senha.append(conta.get_numero())
        
        if sem_senha:
            print(f"Contas sem senha: {sem_senha}")
        else:
            print("Todas as contas possuem senha hash")

    def verificar_integridade_senhas(self):
        """Verifica se todas as contas têm senha_hash válido"""
        for conta in self._contas:
            if not hasattr(conta, 'senha_hash'):
                print(f"ERRO: Conta {conta.get_numero()} não tem atributo senha_hash!")
                conta.senha_hash = ""
            elif not conta.senha_hash:
                print(f"AVISO: Conta {conta.get_numero()} tem senha_hash vazio")

    def _salvar_dados(self):
        """Salva dados no arquivo JSON com tratamento de erros"""
        try:
            for conta in self._contas:
                if isinstance(conta, ContaPoupanca):
                    conta._rodando = False
            
            for conta in self._contas:
                if not hasattr(conta, 'senha_hash'):
                    conta.senha_hash = ""
            
            dados = {
                'usuarios': [u.to_dict() for u in self._usuarios],
                'contas': [self._conta_to_dict(c) for c in self._contas],
                'ultimo_numero_conta': self._ultimo_numero_conta
            }
            
            self.db_manager.save_data(dados)
            
            for conta in self._contas:
                if isinstance(conta, ContaPoupanca) and not conta._rodando:
                    conta._rodando = True
                    if conta._thread_rendimento is None or not conta._thread_rendimento.is_alive():
                        conta._iniciar_rendimento_automatico()
                    
        except Exception as e:
            print(f"ERRO AO SALVAR DADOS: {str(e)}")
            traceback.print_exc()

    def _conta_to_dict(self, conta):
        """Converte objeto Conta para dicionário garantindo que todos os campos são serializáveis."""
        dados = conta.to_dict()
        
        def convert_decimal(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_decimal(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_decimal(item) for item in obj]
            return obj
        
        dados = convert_decimal(dados)
        
        if 'data_ultimo_saque' in dados and dados['data_ultimo_saque']:
            if isinstance(dados['data_ultimo_saque'], date):
                dados['data_ultimo_saque'] = dados['data_ultimo_saque'].strftime("%Y-%m-%d")
        
        if isinstance(conta, ContaPoupanca):
            dados['ultima_atualizacao'] = conta._ultima_atualizacao.strftime("%Y-%m-%d %H:%M:%S")
        
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
        """Cria uma nova conta corrente verificando se já existe uma para o CPF"""
        if not valida_senha(senha, 4):
            raise ValueError("Senha deve ter 4 dígitos")
        
        usuario = self._buscar_usuario(cpf)
        if not usuario:
            raise ValueError("Usuário não encontrado")
        
        # Verifica se já existe conta corrente para este CPF
        for conta in usuario.get_contas():
            if isinstance(conta, ContaCorrente):
                raise ValueError("Este CPF já possui uma conta corrente")
        
        numero = self._proximo_numero_conta()
        conta = ContaCorrente(usuario, numero)
        conta.senha_hash = self._hash_senha(senha)
        
        self._contas.append(conta)
        usuario.add_conta(conta)
        self._salvar_dados()
        
        return conta

    def criar_conta_poupanca(self, cpf, senha):
        """Cria uma nova conta poupança verificando se já existe uma para o CPF"""
        if not valida_senha(senha, 4):
            raise ValueError("Senha deve ter 4 dígitos")
        
        usuario = self._buscar_usuario(cpf)
        if not usuario:
            raise ValueError("Usuário não encontrado")
        
        # Verifica se já existe conta poupança para este CPF
        for conta in usuario.get_contas():
            if isinstance(conta, ContaPoupanca):
                raise ValueError("Este CPF já possui uma conta poupança")
        
        numero = self._proximo_numero_conta()
        conta = ContaPoupanca(usuario, numero)
        conta.senha_hash = self._hash_senha(senha)
        
        self._contas.append(conta)
        usuario.add_conta(conta)
        self._salvar_dados()
        
        return conta

    def usuario_pode_criar_conta(self, cpf, tipo_conta):
        """Verifica se o usuário pode criar o tipo de conta especificado"""
        usuario = self._buscar_usuario(cpf)
        if not usuario:
            return True  
        
        for conta in usuario.get_contas():
            if tipo_conta == 'corrente' and isinstance(conta, ContaCorrente):
                return False
            if tipo_conta == 'poupanca' and isinstance(conta, ContaPoupanca):
                return False
        
        return True
         
    def acessar_conta(self, cpf, agencia, numero, senha):
        """Autentica uma conta com tratamento melhorado"""
        try:
            cpf_limpo = cpf.replace(".", "").replace("-", "")
            senha_hash = self._hash_senha(senha)
            
            for conta in self._contas:
                conta_cpf = conta.get_cliente().get_cpf().replace(".", "").replace("-", "")
                
                if conta_cpf == cpf_limpo and conta.get_numero() == numero:
                    # Debug
                    print(f"Hash armazenado: {conta.senha_hash}")
                    print(f"Hash fornecido: {senha_hash}")
                    
                    if not conta.senha_hash:
                        print("AVISO: Conta sem senha_hash definido!")
                        return None
                    
                    if conta.senha_hash == senha_hash:
                        return conta
                    else:
                        print("Senha não corresponde")
                        return None
            
            print("Conta não encontrada")
            return None
        except Exception as e:
            print(f"Erro ao acessar conta: {str(e)}")
            return None
        
    def corrigir_contas_sem_senha(self, senha_padrao="0000"):
        """Corrige contas sem senha definida"""
        for conta in self._contas:
            if not hasattr(conta, 'senha_hash') or not conta.senha_hash:
                print(f"Corrigindo conta {conta.get_numero()}") 
                conta.senha_hash = self._hash_senha(senha_padrao)
        self._salvar_dados()