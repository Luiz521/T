from banco import Banco
from transacao import Deposito, Saque
from conta import ContaPoupanca

def menu_banco():
    print("\n========== Menu Principal ========")
    print("1. Criar usuario")
    print("2. Criar Conta Corrente")
    print("3. Criar Conta Poupança")
    print("4. Acessar conta")
    print("9. Sair")
    
def menu_operacoes():
    print("\n========== Sistema Bancario ========")
    print("1. Deposito")
    print("2. Saque")
    print("3. Extrato")
    print("9. Sair")
    

def main():
    banco = Banco()
    while True:
        menu_banco()
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            banco.criar_usuario()
        elif opcao == "2":
            banco.criar_conta_corrente()
        elif opcao == "3":
            banco.criar_conta_poupanca()
        elif opcao == "4":
            conta = banco.acessar_conta()
            if conta:
                while True:
                    menu_operacoes()
                    tipo_conta = isinstance(conta, ContaPoupanca)
                
                    opcao_conta = input("Escolha uma opção: ")
                    
                    if opcao_conta == "1":
                        while True: 
                            try:
                                valor = float(input("\nValor do deposito: "))
                                if valor > 0:
                                    break
                                else:
                                    print("Erro: O valor do deposito deve ser positivo.")
                            except ValueError:
                                print("Erro: Digite um valor numero valido")
                        
                        if tipo_conta:
                            conta.calcular_rendimento()
                        transacao = Deposito(valor)
                        conta.realiza_transacao(transacao)
                    elif opcao_conta == "2":
                        while True: 
                            try:
                                valor = float(input("\nValor do saque: "))
                                if valor > 0:
                                    break
                                else:
                                    print("Erro: O valor do saque deve ser positivo.")
                            except ValueError:
                                print("Erro: Digite um valor numero valido")
                        if tipo_conta:
                            conta.calcular_rendimento()
                        transacao = Saque(valor)
                        conta.realiza_transacao(transacao)
                    elif opcao_conta == "3":
                        if tipo_conta:
                            conta.calcular_rendimento()
                        conta.extrato()
                    elif opcao_conta == "9":
                        break
                    else:
                        print("\nErro: Opção invalida.")

        elif opcao == "9":
            break
        else:
            print("\nErro: Opção invalida.")

if __name__ == "__main__":
    main()
    