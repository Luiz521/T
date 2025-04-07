from datetime import datetime
from typing import Union
from decimal import Decimal

from conta import Conta

class Transacao:
    """Classe abstrata base para todas as transações bancárias."""
    
    def get_valor(self) -> Decimal:
        """Retorna o valor da transação."""
        raise NotImplementedError("Método get_valor deve ser implementado")
    
    def registrar(self, conta: 'Conta') -> bool:
        """Registra a transação na conta especificada.
        
        Args:
            conta: Conta onde a transação será registrada
            
        Returns:
            bool: True se a transação foi bem-sucedida, False caso contrário
        """
        raise NotImplementedError("Método registrar deve ser implementado")
    
    def _validar_valor(self, valor: Union[float, Decimal, int]) -> Decimal:
        """Valida e converte o valor para Decimal."""
        if isinstance(valor, Decimal):
            return valor
        try:
            valor_decimal = Decimal(str(valor)).quantize(Decimal('0.01'))
            if valor_decimal <= 0:
                raise ValueError("Valor deve ser positivo")
            return valor_decimal
        except:
            raise ValueError("Valor da transação inválido")

class Deposito(Transacao):
    """Representa uma transação de depósito em conta."""
    
    def __init__(self, valor: Union[float, Decimal, int]):
        """
        Inicializa um depósito com valor positivo.
        
        Args:
            valor: Valor a ser depositado (deve ser positivo)
            
        Raises:
            ValueError: Se o valor for inválido ou não positivo
        """
        self._valor = self._validar_valor(valor)
        self._data = datetime.now()
    
    def get_valor(self) -> Decimal:
        """Retorna o valor do depósito."""
        return self._valor
    
    def registrar(self, conta: 'Conta') -> bool:
        """Registra o depósito na conta especificada."""
        try:
            if conta.depositar(self._valor):
                conta.get_historico().adicionar_transacao(self)
                print(f"\n✅ Depósito de R$ {self._valor:.2f} realizado com sucesso!")
                return True
                
            print("\n❌ Falha ao realizar depósito.")
            return False
        except Exception as e:
            print(f"\n❌ Erro no depósito: {str(e)}")
            return False

class Saque(Transacao):
    """Representa uma transação de saque em conta."""
    
    def __init__(self, valor: Union[float, Decimal, int]):
        """
        Inicializa um saque com valor positivo.
        
        Args:
            valor: Valor a ser sacado (deve ser positivo)
            
        Raises:
            ValueError: Se o valor for inválido ou não positivo
        """
        self._valor = self._validar_valor(valor)
        self._data = datetime.now()
    
    def get_valor(self) -> Decimal:
        """Retorna o valor do saque."""
        return self._valor
    
    def registrar(self, conta: 'Conta') -> bool:
        """Registra o saque na conta especificada."""
        try:
            if conta.sacar(self._valor):
                conta.get_historico().adicionar_transacao(self)
                print(f"\n✅ Saque de R$ {self._valor:.2f} realizado com sucesso!")
                return True
            
            print("\n❌ Saldo insuficiente ou limite de saques excedido")
            return False
        except Exception as e:
            print(f"\n❌ Erro ao realizar saque: {str(e)}")
            return False

class Transferencia(Transacao):
    """Representa uma transação de transferência entre contas."""
    
    def __init__(self, valor: Union[float, Decimal, int], conta_destino: 'Conta'):
        """
        Inicializa uma transferência.
        
        Args:
            valor: Valor a ser transferido (deve ser positivo)
            conta_destino: Conta de destino da transferência
            
        Raises:
            ValueError: Se o valor for inválido ou não positivo
        """
        self._valor = self._validar_valor(valor)
        self._conta_destino = conta_destino
        self._data = datetime.now()
    
    def get_valor(self) -> Decimal:
        """Retorna o valor da transferência."""
        return self._valor
    
    def registrar(self, conta_origem: 'Conta') -> bool:
        """Registra a transferência na conta de origem e destino."""
        try:
            if conta_origem.transferir(self._valor, self._conta_destino):
                conta_origem.get_historico().adicionar_transacao(self)
                self._conta_destino.get_historico().adicionar_transacao(self)
                print(f"\n✅ Transferência de R$ {self._valor:.2f} realizada com sucesso!")
                return True
            
            print("\n❌ Saldo insuficiente para transferência")
            return False
        except Exception as e:
            print(f"\n❌ Erro ao realizar transferência: {str(e)}")
            return False