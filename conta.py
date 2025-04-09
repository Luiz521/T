from datetime import datetime
from decimal import Decimal
import hashlib
import os
import threading
import time
from datetime import datetime

class Historico:
    """Classe responsável por registrar e gerenciar o histórico de transações da conta."""
    
    def __init__(self):
        self._transacoes = []
    
    def adicionar_transacao(self, transacao):
        """Adiciona uma transação ao histórico com data e hora."""
        self._transacoes.append({
            'tipo': transacao.__class__.__name__,
            'valor': transacao.get_valor(),
            'data': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })
    
    def gerar_extrato(self, saldo_atual):
        """Gera um extrato formatado com todas as transações e saldo atual."""
        extrato = "\n========== EXTRATO ==========\n"
        if not self._transacoes:
            extrato += "Não foram realizadas movimentações.\n"
        else:
            for transacao in self._transacoes:
                extrato += (f"{transacao['data']} - {transacao['tipo']}: "
                           f"R$ {transacao['valor']:.2f}\n")
        extrato += f"\nSaldo atual: R$ {saldo_atual:.2f}\n"
        extrato += "==========================="
        return extrato
    
    def get_transacoes(self):
        """Retorna a lista de transações."""
        return self._transacoes

class Conta:
    """Classe base para contas bancárias."""
    
    def __init__(self, cliente, numero):
        self._cliente = cliente
        self._numero = numero
        self._saldo = 0.0
        self._historico = Historico()
        self.senha_hash = None  # Agora armazena apenas o hash da senha
    
    def get_numero(self):
        """Retorna o número da conta."""
        return self._numero
    
    def get_cliente(self):
        """Retorna o cliente titular da conta."""
        return self._cliente
    
    def get_saldo(self):
        """Retorna o saldo atual da conta."""
        return self._saldo
    
    def get_historico(self):
        """Retorna o histórico de transações."""
        return self._historico
    
    def verificar_senha(self, senha):
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        if not self.senha_hash:
            return False
        # Implementação simplificada - considerar usar bcrypt na versão final
        return self.senha_hash == hashlib.sha256(senha.encode()).hexdigest()
    
    def depositar(self, valor):
        """Realiza um depósito na conta com validação"""
        try:
            if not isinstance(valor, (int, float, Decimal)):
                raise ValueError("Valor deve ser numérico")
                
            valor = Decimal(str(valor)).quantize(Decimal('0.01'))
            
            if valor <= 0:
                raise ValueError("Valor do depósito deve ser positivo")
                
            self._saldo += float(valor)  # Conversão explícita para float
            return True
            
        except Exception as e:
            print(f"Erro no depósito: {str(e)}")
            raise  # Re-lança a exceção para ser tratada no nível superior
    
    def sacar(self, valor):
        """Realiza um saque na conta com tratamento de tipos"""
        try:
            # Converte para Decimal se não for
            if not isinstance(valor, Decimal):
                valor = Decimal(str(valor)).quantize(Decimal('0.01'))
            
            if valor <= 0:
                raise ValueError("Valor do saque deve ser positivo")
                
            valor_float = float(valor)  # Converte para float para operação
            if self._saldo >= valor_float:
                self._saldo -= valor_float
                return True
            return False
            
        except Exception as e:
            print(f"Erro no saque: {str(e)}")
            raise
    
    def transferir(self, valor, conta_destino):
        """Realiza uma transferência para outra conta."""
        if self.sacar(valor):
            if conta_destino.depositar(valor):
                return True
            # Se o depósito falhar, devolve o valor
            self._saldo += valor
        return False
    
    def realizar_transacao(self, transacao):
        """Registra uma transação na conta."""
        return transacao.registrar(self)
    
    def gerar_extrato(self):
        """Gera o extrato da conta."""
        return self._historico.gerar_extrato(self._saldo)
    
    def to_dict(self):
        """Converte os dados da conta para dicionário (para persistência)."""
        return {
            'numero': self._numero,
            'cpf_cliente': self._cliente.get_cpf(),
            'saldo': float(self._saldo),  
            'senha_hash': self.senha_hash
        }

class ContaCorrente(Conta):
    """Classe que representa uma conta corrente com limite básico."""
    
    def __init__(self, cliente, numero, limite=500.0, limite_saques=3):
        super().__init__(cliente, numero)
        self._limite = limite
        self._limite_saques = limite_saques
        self._saques_realizados = 0
        self._data_ultimo_saque = None
        self._emprestimos = []  # Lista de empréstimos
        
    def get_limite(self):
        """Retorna o limite da conta."""
        return self._limite
    
    def set_limite(self, novo_limite):
        """Define um novo limite para a conta."""
        if novo_limite >= 0:
            self._limite = novo_limite
            return True
        return False
    
    def sacar(self, valor):
        """Realiza um saque na conta corrente, considerando o limite."""
        hoje = datetime.now().date()
        
        # Reinicia contador de saques se for um novo dia
        if self._data_ultimo_saque != hoje:
            self._saques_realizados = 0
            self._data_ultimo_saque = hoje
        
        if self._saques_realizados >= self._limite_saques:
            raise ValueError("Limite diário de saques atingido")
        
        if valor <= 0:
            raise ValueError("Valor do saque deve ser positivo")
        
        # Verifica se o saque está dentro do limite (saldo + limite)
        if valor > (self._saldo + self._limite):
            raise ValueError("Saldo insuficiente (incluindo limite)")
        
        self._saldo -= valor
        self._saques_realizados += 1
        return True
    
    def solicitar_emprestimo(self, valor, parcelas):
        """Solicita um empréstimo."""
        if valor <= 0:
            raise ValueError("Valor do empréstimo deve ser positivo")
        if parcelas <= 0:
            raise ValueError("Número de parcelas deve ser positivo")
            
        # Simples verificação de crédito - poderia ser mais complexo
        if valor > self._limite * 5:
            raise ValueError("Valor do empréstimo excede seu limite")
            
        emprestimo = {
            'valor': valor,
            'parcelas': parcelas,
            'data': datetime.now(),
            'parcelas_pagas': 0,
            'valor_pago': 0.0
        }
        self._emprestimos.append(emprestimo)
        self._saldo += valor
        return True
    
    def get_emprestimos(self):
        """Retorna lista de empréstimos."""
        return self._emprestimos.copy()
    
    def to_dict(self):
        """Converte os dados da conta corrente para dicionário."""
        dados = super().to_dict()
        dados.update({
            'tipo': 'corrente',
            'limite': self._limite,
            'limite_saques': self._limite_saques,
            'saques_realizados': self._saques_realizados,
            'data_ultimo_saque': self._data_ultimo_saque.strftime("%Y-%m-%d") if self._data_ultimo_saque else None,
            'emprestimos': self._emprestimos
        })
        return dados

class ContaPoupanca(Conta):
    """Classe que representa uma conta poupança com rendimento em tempo real."""
    
    def __init__(self, cliente, numero, taxa_rendimento=0.05):  # 5% por minuto
        super().__init__(cliente, numero)
        self._taxa_rendimento = taxa_rendimento
        self._ultima_atualizacao = datetime.now()
        self._thread_rendimento = None
        self._rodando = False
        self._iniciar_rendimento_automatico()
    
    def _iniciar_rendimento_automatico(self):
        """Inicia a thread que calcula rendimentos automaticamente."""
        if self._thread_rendimento is None:
            self._rodando = True
            self._thread_rendimento = threading.Thread(
                target=self._calcular_rendimento_continuo, 
                daemon=True
            )
            self._thread_rendimento.start()
    
    def _calcular_rendimento_continuo(self):
        """Calcula rendimentos a cada minuto enquanto a conta existir."""
        while self._rodando:
            time.sleep(60)  # Espera 1 minuto
            self._aplicar_rendimento()
    
    def _aplicar_rendimento(self):
        """Aplica o rendimento de 5% sobre o saldo atual."""
        with threading.Lock():  # Previne condições de corrida
            if self._saldo > 0:  # Só aplica rendimento se houver saldo positivo
                rendimento = self._saldo * self._taxa_rendimento
                self._saldo += rendimento
                self._ultima_atualizacao = datetime.now()
                
                # Adiciona ao histórico como uma transação especial
                transacao = {
                    'tipo': 'Rendimento',
                    'valor': rendimento,
                    'data': self._ultima_atualizacao.strftime("%d/%m/%Y %H:%M:%S")
                }
                self._historico._transacoes.append(transacao)
    
    def encerrar(self):
        """Encerra a thread de rendimento automático."""
        self._rodando = False
        if self._thread_rendimento:
            self._thread_rendimento.join()
    
    def get_saldo(self):
        """Retorna o saldo atual, garantindo thread safety."""
        with threading.Lock():
            return self._saldo
    
    def to_dict(self):
        """Converte os dados para dicionário (serialização)."""
        dados = super().to_dict()
        dados.update({
            'tipo': 'poupanca',
            'taxa_rendimento': self._taxa_rendimento,
            'data_ultimo_rendimento': self._ultima_atualizacao.strftime("%Y-%m-%d %H:%M:%S"),
            'minutos_acumulados': getattr(self, '_minutos_acumulados', 0)  # Campo adicional se existir
        })
        return dados