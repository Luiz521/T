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
        self.senha_hash = ""  
    
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
                
            self._saldo = float(Decimal(str(self._saldo)) + valor)
            self._salvar_atualizacao() 
            return True
            
        except Exception as e:
            print(f"Erro no depósito: {str(e)}")
            raise

    def _salvar_atualizacao(self):
        """Força a atualização dos dados no banco"""
        if hasattr(self, '_banco'):
            self._banco._salvar_dados()   
    
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
            'cpf_cliente': self._cliente.get_cpf().replace(".", "").replace("-", ""), 
            'saldo': float(self._saldo),
            'senha_hash': getattr(self, 'senha_hash', ""), 
            'historico': [transacao for transacao in self._historico.get_transacoes()]  
        }
class ContaCorrente(Conta):
    """Classe que representa uma conta corrente com limite básico."""
    
    def __init__(self, cliente, numero, limite=500.0, limite_saques=3):
        super().__init__(cliente, numero)
        self._limite = limite
        self._limite_saques = limite_saques
        self._saques_realizados = 0
        self._data_ultimo_saque = None
        self._emprestimos = []  
        
    def sacar(self, valor):
        """Realiza um saque na conta corrente, considerando o limite."""
        try:
            if not isinstance(valor, Decimal):
                valor = Decimal(str(valor)).quantize(Decimal('0.01'))
            
            hoje = datetime.now().date()
            
            if self._data_ultimo_saque != hoje:
                self._saques_realizados = 0
                self._data_ultimo_saque = hoje
            
            if self._saques_realizados >= self._limite_saques:
                raise ValueError("Limite diário de saques atingido")
            
            if valor <= 0:
                raise ValueError("Valor do saque deve ser positivo")
            
            saldo_decimal = Decimal(str(self._saldo))
            limite_decimal = Decimal(str(self._limite))
            
            if valor > (saldo_decimal + limite_decimal):
                raise ValueError("Saldo insuficiente (incluindo limite)")
            
            self._saldo = float(saldo_decimal - valor)
            self._saques_realizados += 1
            
            if hasattr(self, '_banco'):
                self._banco._salvar_dados()
                
            return True
            
        except Exception as e:
            print(f"Erro no saque: {str(e)}")
            raise
        
    def get_limite(self):
        """Retorna o limite da conta."""
        return self._limite
    
    def set_limite(self, novo_limite):
        """Define um novo limite para a conta."""
        if novo_limite >= 0:
            self._limite = novo_limite
            return True
        return False
    
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
        dados = super().to_dict()
        dados.update({
            'tipo': 'corrente',
            'limite': float(self._limite),
            'limite_saques': int(self._limite_saques),
            'saques_realizados': int(self._saques_realizados),
            'data_ultimo_saque': self._data_ultimo_saque.strftime("%Y-%m-%d") if self._data_ultimo_saque else None,
            'emprestimos': self._emprestimos
        })
        return dados

class ContaPoupanca(Conta):
    def __init__(self, cliente, numero, taxa_rendimento=0.05):
        super().__init__(cliente, numero)
        self._taxa_rendimento = taxa_rendimento
        self._ultima_atualizacao = datetime.now()
        self._thread_rendimento = None
        self._rodando = False
        self.senha_hash = ""
        
        self._iniciar_rendimento_automatico()
    
    def _aplicar_rendimento(self):
        """Aplica o rendimento com tratamento de erros"""
        try:
            if self._saldo > 0:
                rendimento = self._saldo * self._taxa_rendimento
                self._saldo += rendimento
                self._ultima_atualizacao = datetime.now()
                
                transacao = {
                    'tipo': 'Rendimento',
                    'valor': rendimento,
                    'data': self._ultima_atualizacao.strftime("%d/%m/%Y %H:%M:%S")
                }
                self._historico._transacoes.append(transacao)
                
                if hasattr(self, '_banco'):
                    try:
                        self._banco._salvar_dados()
                    except Exception as e:
                        print(f"Erro ao salvar rendimento: {str(e)}")
        except Exception as e:
            print(f"Erro ao aplicar rendimento: {str(e)}")
    
    def _iniciar_rendimento_automatico(self):
        """Inicia a thread que calcula rendimentos automaticamente."""
        if not self._rodando:
            self._rodando = True
            self._thread_rendimento = threading.Thread(
                target=self._calcular_rendimento_continuo, 
                daemon=True
            )
            self._thread_rendimento.start()
    
    def _calcular_rendimento_continuo(self):
        """Calcula rendimentos a cada minuto enquanto a conta existir."""
        while self._rodando:
            time.sleep(60)  # 60 segundos
            self._aplicar_rendimento()
    
    def encerrar(self):
        """Encerra a thread de rendimento automático."""
        self._rodando = False
        if self._thread_rendimento and self._thread_rendimento != threading.current_thread():
            self._thread_rendimento.join(timeout=1)
        self._salvar_imediato()


    def _salvar_imediato(self):
        """Força o salvamento imediato dos dados"""
        if hasattr(self, '_banco'):
            self._banco._salvar_dados()
            print("Dados da poupança salvos imediatamente")  
    
    def get_saldo(self):
        """Retorna o saldo atual, garantindo thread safety."""
        with threading.Lock():
            return self._saldo
    
    def to_dict(self):
        dados = super().to_dict()
        dados.update({
            'tipo': 'poupanca',
            'taxa_rendimento': float(self._taxa_rendimento),
            'ultima_atualizacao': self._ultima_atualizacao.strftime("%Y-%m-%d %H:%M:%S"),
            'saldo': float(self._saldo)
        })
        return dados