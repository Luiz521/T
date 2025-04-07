from datetime import datetime
from typing import List, Dict, Optional, Union
from transacao import Deposito, Saque, Transferencia

class Historico:
    """Classe responsável por registrar e gerenciar o histórico de transações bancárias.
    
    Attributes:
        _transacoes (List[Dict]): Lista de transações registradas, cada uma representada como um dicionário
                                  contendo 'tipo', 'valor' e 'data'.
    """
    
    def __init__(self):
        """Inicializa um novo histórico com lista vazia de transações."""
        self._transacoes: List[Dict[str, Union[str, float]]] = []
    
    def adicionar_transacao(self, transacao: Union[Deposito, Saque, Transferencia]) -> None:
        """Registra uma nova transação no histórico com data/hora atual.
        
        Args:
            transacao: Objeto de transação (Deposito, Saque ou Transferencia)
            
        Raises:
            ValueError: Se o objeto transação for inválido
        """
        if not hasattr(transacao, 'get_valor') or not hasattr(transacao, '__class__'):
            raise ValueError("Objeto de transação inválido")
            
        self._transacoes.append({
            'tipo': transacao.__class__.__name__,
            'valor': transacao.get_valor(),
            'data': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })
    
    def to_dict(self) -> List[Dict]:
        """Converte o histórico para lista de dicionários serializável.
        
        Returns:
            Lista de transações no formato de dicionário
        """
        return self._transacoes.copy()
    
    def get_transacoes(self) -> List[Dict]:
        """Retorna uma cópia da lista de transações.
        
        Returns:
            Lista de todas as transações registradas
        """
        return self._transacoes.copy()
    
    def get_ultimo_deposito(self) -> Optional[Dict]:
        """Obtém o último depósito registrado no histórico.
        
        Returns:
            Dicionário com informações do último depósito ou None se não houver
        """
        for transacao in reversed(self._transacoes):
            if transacao['tipo'] == 'Deposito':
                return transacao.copy()
        return None
    
    def filtrar_por_tipo(self, tipo: str) -> List[Dict]:
        """Filtra transações por tipo (Deposito, Saque, Transferencia).
        
        Args:
            tipo: Tipo de transação a filtrar
            
        Returns:
            Lista de transações filtradas
        """
        return [t.copy() for t in self._transacoes if t['tipo'] == tipo]
    
    def extrato(self, num_ultimas: int = 10) -> str:
        """Gera um extrato formatado das últimas transações.
        
        Args:
            num_ultimas: Número de transações a incluir no extrato
            
        Returns:
            String formatada com o extrato
        """
        extrato = []
        for t in self._transacoes[-num_ultimas:]:
            extrato.append(f"{t['data']} - {t['tipo']}: R$ {t['valor']:.2f}")
        return "\n".join(extrato) if extrato else "Nenhuma transação registrada"
    
    def saldo_atual(self) -> float:
        """Calcula o saldo atual baseado nas transações registradas.
        
        Returns:
            Saldo calculado (soma de depósitos menos saques e transferências)
        """
        saldo = 0.0
        for t in self._transacoes:
            if t['tipo'] == 'Deposito':
                saldo += t['valor']
            else:  # Saque ou Transferencia
                saldo -= t['valor']
        return saldo