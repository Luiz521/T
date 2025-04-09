from datetime import datetime
from typing import List, Dict
import re

from conta import Conta

class Pessoa:
    """Classe que representa uma pessoa com dados básicos e validações."""
    
    def __init__(self, nome: str, cpf: str, data_nascimento: str, endereco: str):
        """
        Inicializa uma pessoa com dados validados.
        
        Args:
            nome: Nome completo
            cpf: CPF (apenas números)
            data_nascimento: Data no formato DD/MM/AAAA
            endereco: Endereço completo
            
        Raises:
            ValueError: Se algum dado for inválido
        """
        self.set_nome(nome)
        self.set_cpf(cpf)
        self.set_data_nascimento(data_nascimento)
        self.set_endereco(endereco)
    
    def get_nome(self) -> str:
        """Retorna o nome completo."""
        return self._nome
    
    def set_nome(self, nome: str) -> None:
        """Define o nome com validação."""
        if not nome or not all(c.isalpha() or c.isspace() for c in nome):
            raise ValueError("Nome deve conter apenas letras e espaços")
        self._nome = nome.strip()
    
    def get_cpf(self) -> str:
        """Retorna o CPF formatado."""
        return f"{self._cpf[:3]}.{self._cpf[3:6]}.{self._cpf[6:9]}-{self._cpf[9:]}"
    
    def set_cpf(self, cpf: str) -> None:
        """Define o CPF com validação."""
        cpf = re.sub(r'[^0-9]', '', cpf)
        if len(cpf) != 11 or not cpf.isdigit():
            raise ValueError("CPF deve conter 11 dígitos")
        self._cpf = cpf
    
    def get_data_nascimento(self) -> str:
        """Retorna a data de nascimento formatada."""
        return self._data_nascimento
    
    def set_data_nascimento(self, data_nascimento: str) -> None:
        """Define a data de nascimento com validação."""
        try:
            nasc = datetime.strptime(data_nascimento, "%d/%m/%Y")
            idade = (datetime.now() - nasc).days // 365
            if idade < 18:
                raise ValueError("Deve ter 18 anos ou mais")
        except ValueError:
            raise ValueError("Data deve estar no formato DD/MM/AAAA")
        self._data_nascimento = data_nascimento
    
    def get_endereco(self) -> str:
        """Retorna o endereço completo."""
        return self._endereco
    
    def set_endereco(self, endereco: str) -> None:
        """Define o endereço com validação básica."""
        if not endereco or len(endereco) < 10:
            raise ValueError("Endereço muito curto")
        self._endereco = endereco.strip()
    
    def get_idade(self) -> int:
        """Calcula e retorna a idade em anos."""
        nasc = datetime.strptime(self._data_nascimento, "%d/%m/%Y")
        return (datetime.now() - nasc).days // 365
    
    def to_dict(self) -> Dict:
        """Converte os dados para dicionário (serializável)."""
        return {
            'nome': self._nome,
            'cpf': self._cpf,  # Armazenado sem formatação
            'data_nascimento': self._data_nascimento,
            'endereco': self._endereco
        }

class Usuario(Pessoa):
    """Classe que representa um usuário do banco com contas associadas."""
    
    def __init__(self, nome: str, cpf: str, data_nascimento: str, endereco: str):
        super().__init__(nome, cpf, data_nascimento, endereco)
        self._contas: List['Conta'] = []  # Referência a objetos Conta
    
    def get_contas(self) -> List['Conta']:
        """Retorna lista de contas do usuário."""
        return self._contas.copy()  # Retorna cópia para evitar modificações externas
        
    def add_conta(self, conta: 'Conta') -> None:
        if not hasattr(conta, 'get_numero'):
            raise ValueError("Objeto conta inválido")
            
        for c in self._contas:
            if type(c) == type(conta): 
                raise ValueError(f"Usuário já possui uma conta do tipo {type(conta).__name__}")
                
        self._contas.append(conta)
    
    def remover_conta(self, numero_conta: int) -> bool:
        """Remove uma conta pelo número."""
        for i, conta in enumerate(self._contas):
            if conta.get_numero() == numero_conta:
                self._contas.pop(i)
                return True
        return False
    
    def to_dict(self) -> Dict:
        """Converte os dados para dicionário, incluindo contas."""
        dados = super().to_dict()
        dados['contas'] = [c.get_numero() for c in self._contas]
        return dados
    
    def __str__(self) -> str:
        """Representação textual do usuário."""
        return f"Usuário: {self.get_nome()} (CPF: {self.get_cpf()})"