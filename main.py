from banco import Banco
from banco import Banco
from transacao import Deposito, Saque, Transferencia
from conta import ContaPoupanca, ContaCorrente
from utils import valida_senha, valida_cpf

def menu_banco():
    print("\n========== Menu Principal ========")
    print("1. Criar usuário")
    print("2. Criar Conta Corrente")
    print("3. Criar Conta Poupança")
    print("4. Acessar conta")
    print("5. Listar usuários")
    print("6. Listar contas")
    print("9. Sair")

def menu_operacoes():
    print("\n========== Operações Bancárias ========")
    print("1. Depósito")
    print("2. Saque")
    print("3. Transferência")
    print("4. Extrato")
    print("5. Calcular rendimento (Poupança)")
    print("9. Voltar")

def ler_valor(mensagem):
    while True:
        try:
            valor = float(input(mensagem))
            if valor > 0:
                return valor
            print("Erro: O valor deve ser positivo.")
        except ValueError:
            print("Erro: Digite um valor numérico válido.")

def ler_cpf():
    while True:
        cpf = input("CPF (apenas números): ")
        if valida_cpf(cpf):
            return cpf
        print("CPF inválido! Deve conter 11 dígitos.")

def ler_senha():
    while True:
        senha = input("Senha (4 dígitos): ")
        if valida_senha(senha, 4):
            return senha
        print("Senha inválida! Deve conter exatamente 4 dígitos.")

def main():
    banco = Banco()
    
    while True:
        menu_banco()
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":  # Criar usuário
            print("\n--- Cadastro de Usuário ---")
            nome = input("Nome completo: ")
            cpf = ler_cpf()
            data_nasc = input("Data de nascimento (DD/MM/AAAA): ")
            endereco = input("Endereço (logradouro, nro - bairro - cidade/UF): ")
            
            try:
                banco.criar_usuario(nome, cpf, data_nasc, endereco)
                print("Usuário cadastrado com sucesso!")
            except ValueError as e:
                print(f"Erro: {str(e)}")
                
        elif opcao == "2":  # Criar Conta Corrente
            print("\n--- Criar Conta Corrente ---")
            cpf = ler_cpf()
            senha = ler_senha()
            
            try:
                conta = banco.criar_conta_corrente(cpf, senha)
                print(f"Conta corrente criada com sucesso! Número: {conta.get_numero_conta()}")
            except ValueError as e:
                print(f"Erro: {str(e)}")
                
        elif opcao == "3":  # Criar Conta Poupança
            print("\n--- Criar Conta Poupança ---")
            cpf = ler_cpf()
            senha = ler_senha()
            
            try:
                conta = banco.criar_conta_poupanca(cpf, senha)
                print(f"Conta poupança criada com sucesso! Número: {conta.get_numero_conta()}")
            except ValueError as e:
                print(f"Erro: {str(e)}")
                
        elif opcao == "4":  # Acessar conta
            print("\n--- Acessar Conta ---")
            cpf = ler_cpf()
            senha = input("Senha da conta: ")
            
            try:
                numero_conta = int(input("Número da conta: "))
                conta = banco.acessar_conta(cpf, "0001", numero_conta, senha)
                
                if conta:
                    while True:
                        menu_operacoes()
                        opcao_conta = input("Escolha uma opção: ")
                        
                        if opcao_conta == "1":  # Depósito
                            valor = ler_valor("Valor do depósito: R$ ")
                            transacao = Deposito(valor)
                            conta.realiza_transacao(transacao)
                            
                        elif opcao_conta == "2":  # Saque
                            valor = ler_valor("Valor do saque: R$ ")
                            transacao = Saque(valor)
                            conta.realiza_transacao(transacao)
                            
                        elif opcao_conta == "3":  # Transferência
                            valor = ler_valor("Valor da transferência: R$ ")
                            numero_destino = int(input("Número da conta destino: "))
                            
                            conta_destino = None
                            for c in banco.get_contas():
                                if c.get_numero_conta() == numero_destino:
                                    conta_destino = c
                                    break
                            
                            if conta_destino:
                                transacao = Transferencia(valor, conta_destino)
                                conta.realiza_transacao(transacao)
                            else:
                                print("Conta destino não encontrada!")
                                
                        elif opcao_conta == "4":  # Extrato
                            conta.extrato()
                            
                        elif opcao_conta == "5":  # Calcular rendimento
                            if isinstance(conta, ContaPoupanca):
                                conta.calcular_rendimento()
                                print("Rendimento calculado e aplicado!")
                            else:
                                print("Esta opção é válida apenas para contas poupança!")
                                
                        elif opcao_conta == "9":  # Voltar
                            break
                            
                        else:
                            print("Opção inválida!")
                else:
                    print("Conta não encontrada ou senha incorreta!")
            except ValueError:
                print("Erro: Número da conta deve ser um valor inteiro.")
                
        elif opcao == "5":  # Listar usuários
            print("\n--- Usuários Cadastrados ---")
            for usuario in banco.get_usuarios():
                print(f"Nome: {usuario.get_nome()} | CPF: {usuario.get_cpf()} | Contas: {len(usuario.get_contas())}")
                
        elif opcao == "6":  # Listar contas
            print("\n--- Contas Cadastradas ---")
            for conta in banco.get_contas():
                tipo = "Corrente" if isinstance(conta, ContaCorrente) else "Poupança"
                print(f"Número: {conta.get_numero_conta()} | Tipo: {tipo} | Titular: {conta.get_usuario().get_nome()} | Saldo: R$ {conta.get_saldo():.2f}")
                
        elif opcao == "9":  # Sair
            print("Saindo do sistema...")
            break
            
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()