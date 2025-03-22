from utils import valida_nome, valida_data_nascimento, valida_cpf, valida_senha
from pessoa import Usuario
from conta import *

class Banco:
    
    def __init__(self):
        self.usuarios = []
        self.contas = []
        self._add_user_teste()
        
    def _add_user_teste(self):
        novo_usuario = Usuario("Luiz Eduardo", "00000000000", "27/03/1997", "Casa 1")
        self.usuarios.append(novo_usuario)

        conta = ContaCorrente(novo_usuario, "0000")
        self.contas.append(conta)
    
    def criar_usuario(self):
        print("\n========== Cadastro de Novo Usuario ========")
        
        while True:
            nome = input("Nome completo: ")
            if valida_nome(nome):
                break
            
            print("\nErro: Nome invalido! Digite apenas letras.")
            
        while True:
            data_nascimento = input("Data de nascimento (DD/MM/AAAA): ")
            
            if valida_data_nascimento(data_nascimento):
                break
            
            print("\nErro: Data de nascimento invalida ou usuario menor que 18 anos.")
            
        while True:
            cpf = input("CPF (Somente numeros): ")
            cpf_formatado = cpf.replace("-", "").replace(".", "")
            
            if valida_cpf(cpf_formatado) and not any(usuario.cpf == cpf_formatado for usuario in self.usuarios):
                break
            
            print("\nErro: CPF Invalido ou já cadastrado")
            
            
        endereco = input("Endereço (logradouro, numero - bairro - cidade - UF - CEP): ")

        novo_usuario = Usuario(nome, cpf, data_nascimento, endereco)
        self.usuarios.append(novo_usuario)
        print("\nUsuario cadastrado com sucesso!")
            
    def criar_conta_corrente(self):
        print("\n========== Cadastro de Conta Nova Corrente ========")
        
        cpf = input("Informe o CPF do titular da conta: ")
        usuario = next((u for u in self.usuarios if u.cpf == cpf), None)
        
        if not usuario:
            print("\nErro: Usuario não encontrado.")
            return
        
        senha = input("Crie uma senha de 4 digitos: ")
        while not valida_senha(senha, 4):
            print("\nErro: A senha deve conter exatamente 4 digitos numericos")
            senha = input("Crie uma senha de 4 digitos: ")
        
        conta = ContaCorrente(usuario, senha)
        self.contas.append(conta)
        print(f"\nConta criada com sucesso!")
        conta.imprime()
    
    def criar_conta_poupanca(self):
        print("\n========== Cadastro de Nova Conta Poupança ========")

        cpf = input("Informe o CPF do titular da conta: ")
        usuario = next((u for u in self.usuarios if u.cpf == cpf), None)
        
        if not usuario:
            print("\nErro: Usuario não encontrado.")
            return
        
        senha = input("Crie uma senha de 4 digitos: ")
        while not valida_senha(senha, 4):
            print("\nErro: A senha deve conter exatamente 4 digitos numericos")
            senha = input("Crie uma senha de 4 digitos: ")
        
        conta = ContaPoupanca(usuario, senha)
        self.contas.append(conta)
        
        
    def acessar_conta(self):
        print("\n========== Acessa o sistema Bancario ========")
        
        cpf = input("Informe o seu CPF: ")
        contas_usuario = [conta for conta in self.contas if conta.usuario.cpf == cpf]
        
        if not contas_usuario:
            print("\nErro: Nenhuma conta cadastrada para este usuario")
            return None
        
        print("\nContas encontradas: ")
        for conta in contas_usuario:
            conta.imprime()
        
        agencia = input("Informe o numero da agencia: ")
        try:
            numero_conta = int(input("Informe o numero da conta: "))
        except ValueError:
            print("\nErro: Informe sua senha de 4 digitos numerica")
        
        conta = next((conta for conta in contas_usuario if conta.agencia == agencia and conta.numero_conta == numero_conta), None)
        if not conta:
            print("\nErro: Nenhuma conta encontrada com esses dados.")
            
        max_tentativas = 3
        tentativas = 0
        while tentativas < max_tentativas:
            senha = input("Informe sua senha de 4 digitos: ")
            
            if conta.validar_senha(senha):
                return conta
            else:
                tentativas += 1
                print(f"\nErro: Senha incorreta! Tentativas restantes: {max_tentativas - tentativas}.")
                
        print(f"\nErro: Maximo de tentativos excedido.")
        return None