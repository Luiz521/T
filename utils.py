from datetime import datetime

def valida_senha(senha, tamanho):
    return senha.isdigit() and len(senha) == tamanho

def valida_nome(nome):
    return nome.replace(" ", "").isalpha()

def valida_data_nascimento(data_nascimento):
    try:
        data = datetime.strptime(data_nascimento, "%d/%m/%Y")
        idade = (datetime.now() - data).days // 365
    
        return idade >= 18
    except ValueError:
        return False

def valida_cpf(valor):
    cpf_formatado = valor.replace("-", "").replace(".", "")
    return len(cpf_formatado) == 11