from datetime import datetime
from abc import ABC

class Pessoa(ABC):
    """
    Classe abstrata para representar uma pessoa do sistema.
    
    Atributos protegidos:
    - __nome: Nome completo da pessoa.
    - __cpf: CPF da pessoa (apenas numeros).
    - __data_nascimento: Data de nascimento da pessoa no formato "DD/MM/AAAA".
    - __endereco: Endereço completo da pessoa "Logradouro, numero - Bairro - Cidade - Estado - CEP"
    
    Uso do @property:
    - Permite acessar os atributos de forma segura, sem expo-los diretamente.
    - Mantem o principio do encapsulamento, evitando modificações diretas.
    """
    
    def __init__(self, nome, cpf, data_nascimento, endereco):
        self.__nome = nome
        self.__cpf = cpf
        self.__data_nascimento = data_nascimento
        self.__endereco = endereco

    @property
    def nome(self):
        """
        Retorna o nome completo da pessoa.
        """
        return self.__nome

    @nome.setter
    def nome(self, valor):
        self.__nome = valor

    @property
    def cpf(self):
        return self.__cpf

    @cpf.setter
    def cpf(self, valor):
        self.__cpf = valor

    @property
    def data_nascimento(self):
        return self.__data_nascimento

    @data_nascimento.setter
    def data_nascimento(self, data):
        self.__data_nascimento = data

    @property
    def idade(self):
        return (datetime.now() - self.data_nascimento).days // 365
    
    @property
    def endereco(self):
        return self.__endereco
    
    @endereco.setter
    def endereco(self, valor):
        self.__endereco = valor

    def apresentar(self):
        print(f"Nome: {self.nome}, Idade {self.idade}")


class Usuario(Pessoa):
    """Classe concreta de Usuario que herda de pessoa e representa um usuario do sistema bancario."""
    pass