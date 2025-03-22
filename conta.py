from abc import ABC
from historico import Historico
from utils import valida_senha
from datetime import datetime
from transacao import*


class Conta(ABC):
    agencia_padrao = "0001"
    numero_contas = 0
    
    def __init__(self, usuario, senha_4_digitos):
        while not valida_senha(senha_4_digitos, 4):
            print("Senha invalida. A senha deve conter 4 digitos")
            senha_4_digitos = input("Crie uma senha de 4 digitos: ")

        Conta.numero_contas += 1
        self.__agencia = Conta.agencia_padrao
        self.__numero_conta = Conta.numero_contas
        self.__usuario = usuario
        self.__senha_4_digitos = senha_4_digitos
        self.__saldo = 0.0
        self.__historico = Historico()
        
        
    @property
    def agencia(self):
        return self.__agencia
    
    @property
    def numero_conta(self):
        return self.__numero_conta

    @property
    def saldo(self):
        return self.__saldo
    
    @property
    def historico(self):
        return self.__historico
    
    @property
    def usuario(self):
        return self.__usuario
    
    def realiza_transacao(self, transacao):
        transacao.registrar(self)
    
    def add_saldo(self, valor):
        """
        Adiciona saldo na conta
        """
        self.__saldo += valor
        
    def sub_saldo(self, valor):
        """
        Subtrai saldo da conta
        """
        self.__saldo -= valor

    def validar_senha(self, senha):
        return self.__senha_4_digitos == senha
    
    def imprime(self):
        return print(f"Agencia: {self.__agencia} | Conta: {self.__numero_conta} | Tipo: {self.__class__.__name__}")
    
    def extrato(self):
        print("\n================ Extrato ================")
        print(f"Cliente: {self.__usuario.nome}")
        print(f"Agencia: {self.__agencia} | Conta: {self.__numero_conta}")
        print(f"Data Extrato: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        print("----------------------------------------------")
        
        if not self.__historico.transacoes:
            print("Não foram realizadas movimentações")
        else:
            # [11/11/1908 20:00:40] Saque: R$ 200.00
            for transacao in self.__historico.transacoes:
                print(f"[{transacao['data']}] {transacao['tipo']}: R$ {transacao['valor']:.2f}")
        
        print("----------------------------------------------")
        print(f"Saldo: R$ {self.__saldo:.2f}")
        print("===========================================")


class ContaCorrente(Conta):
    """Classe concreta que herda de conta e implementa uma conta bancaria."""
    def __init__(self, usuario, senha, limite_saque=500, max_saques_diario=5):
        super().__init__(usuario, senha)
        self.__numero_saques = 0
        self.__limite_saque = limite_saque
        self.__max_saques_diario = max_saques_diario

    @property
    def numero_saques(self):
        return self.__numero_saques

    @numero_saques.setter
    def numero_saques(self, valor):
        self.__numero_saques = valor

    @property
    def limite_saque(self):
        return self.__limite_saque

    @property
    def max_saques_diario(self):
        return self.__max_saques_diario


class ContaPoupanca(Conta):

    def __init__(self, usuario, senha):
        super().__init__(usuario, senha)
        self.__taxa_rendimento = 0.10  # 10% ao mes
        self.__rendimento = 0.0

    @property
    def taxa_rendimento(self):
        return self.__taxa_rendimento
    
    @property
    def rendimento(self):
        return self.__rendimento
    
    @taxa_rendimento.setter
    def taxa_rendimento(self, valor):
        self.__taxa_rendimento = valor
    
    @rendimento.setter
    def rendimento(self, valor):
        self.__rendimento = valor
    
    def calcular_rendimento(self): #CALCULAR RENDIMENTO NAO TA FUNCIONANDO
        """
        Calcula o rendimento com base no saldo da conta e na taxa de rendimento mensal (10% ao ano).
        O rendimento é aplicado a cada 5 segundos.
        """
        
        # 1. Obter o saldo atual da conta
        saldo_atual = self.saldo  # Aqui você usa a função que calcula o saldo a partir das transações no histórico
        
        # 2. Encontrar o último depósito no histórico
        ultimo_deposito = self.historico.ultimo_deposito
        
        if ultimo_deposito:
            # 3. Calcular o tempo que passou desde o último depósito em segundos
            tempo_passado_em_segundos = (datetime.now() - datetime.strptime(ultimo_deposito['data'], "%d-%m-%Y %H:%M:%S")).total_seconds()
            
            # 4. Verificar se o tempo passou pelo menos 5 segundos para aplicar o rendimento
            if tempo_passado_em_segundos >= 5:
                print("Calculando rendimento da conta poupança...")

                # 5. Calcular o rendimento mensal (exemplo: 10% ao ano)
                # Vamos dividir a taxa de rendimento anual por 12 para obter o rendimento mensal
                taxa_ano = self.__taxa_rendimento  # 10% ao ano
                taxa_mes = taxa_ano / 12  # 10% / 12 meses
                
                # 6. Calcular o rendimento mensal
                rendimento_mensal = saldo_atual * taxa_mes  # Rendimento mensal

                # 7. Ajustar o rendimento para os 5 segundos passados
                # 1 mês tem aproximadamente 30 dias, ou seja, 30 * 24 * 60 * 60 segundos
                # Vamos dividir o rendimento mensal por esses segundos para saber o rendimento por segundo.
                rendimento_por_segundo = rendimento_mensal / (30 * 24 * 60 * 60)  # Por segundo

                # 8. Calcular o rendimento para os 5 segundos passados
                rendimento = rendimento_por_segundo * 5  # Multiplicamos pela quantidade de segundos passados (5 segundos)
                
                # 9. Adicionar o rendimento ao saldo da conta
                self.add_saldo(rendimento)
                
                # 10. Registrar o rendimento no histórico (como um "depósito de rendimento")
                self.historico.add_transacao(Deposito(rendimento))  # Criando um depósito com o valor do rendimento
                print(f"Rendimento de R$ {rendimento:.2f} adicionado na conta.")
