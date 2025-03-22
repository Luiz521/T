from abc import ABC, abstractmethod

class Transacao(ABC):
    """
    Classe abstrata para representar uma transação bancaria.
    """
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @abstractmethod
    def registrar(self, conta):
        """
        Metodo abstrato para registrar a transação em uma conta.
        
        Deve ser implementado por todas as subclasses.
        """
        pass
    
    
class Deposito(Transacao):
    """Classe concreta de Deposito."""
    def __init__(self, valor):
        self.__valor = valor
        
    @property
    def valor(self):
        return self.__valor
    
    def registrar(self, conta):
        if self.__valor > 0:
            conta.add_saldo(self.valor)
            conta.historico.add_transacao(self)
            print(f"\nDeposito de R$ {self.__valor:.2f} realizado com sucesso!")
        else:
            print(f"\nErro: O valor do deposito deve ser positivo.")
            

class Saque(Transacao):
    """Classe concreta de saque."""
    def __init__(self, valor):
        self.__valor = valor
        
    @property
    def valor(self):
        return self.__valor
    
    def registrar(self, conta):
        if self.__valor <= 0:
            print(f"\nErro: O valor do saque deve ser positivo")
        elif self.__valor > conta.saldo:
            print(f"\nErro: Saldo insuficiente")
        elif self.__valor > conta.limite_saque:
            print(f"\nErro: Valor excede o limite de saque da conta")
        elif conta.numero_saques >= conta.max_saques_diario:
            print(f"\nErro: Numero de saques diarios excedido")
        else:
            conta.numero_saques += 1
            conta.sub_saldo(self.__valor)
            conta.historico.add_transacao(self)
            print(f"\nSaque de R$ {self.valor:.2f} realizado com sucesso!")
            

class Transferencia(Transacao):
    pass