from datetime import datetime
from transacao import Deposito

class Historico:
    """Classe que representa o historico de transacoes da conta."""
    def __init__(self):
        self.__transacoes = []

    @property
    def transacoes(self):
        return self.__transacoes
    
    @property
    def ultimo_deposito(self):
        # Retorna a última transação de depósito
        for transacao in reversed(self.transacoes):
            if isinstance(transacao, Deposito):
                return transacao
        return None
    
    def add_transacao(self, transacao):
        self.transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
        )