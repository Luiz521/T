from datetime import datetime
import re

def valida_senha(senha: str, tamanho: int = 4) -> bool:
    """Valida se a senha atende aos requisitos de segurança.
    
    Args:
        senha: Senha a ser validada
        tamanho: Tamanho mínimo requerido (padrão: 4)
        
    Returns:
        bool: True se a senha é válida, False caso contrário
    """
    if not isinstance(senha, str) or not senha.isdigit() or len(senha) != tamanho:
        return False
    
    # Verifica se há sequências óbvias (ex: 1234, 0000, etc.)
    if (senha == senha[0] * tamanho or  # Todos dígitos iguais
        senha in ('1234', '4321', '1111', '0000')):  # Sequências comuns
        return False
    
    return True

def valida_nome(nome: str) -> bool:
    """Valida se o nome contém apenas letras e espaços.
    
    Args:
        nome: Nome completo a ser validado
        
    Returns:
        bool: True se o nome é válido, False caso contrário
    """
    if not isinstance(nome, str) or len(nome.strip()) < 3:
        return False
    
    # Permite letras, espaços e alguns caracteres especiais comuns em nomes
    padrao = r'^[a-zA-ZÀ-ÿ\s\'-]+$'
    return bool(re.fullmatch(padrao, nome.strip()))

def valida_data_nascimento(data_nascimento: str, idade_minima: int = 18) -> bool:
    """Valida a data de nascimento e verifica se a idade mínima foi atingida.
    
    Args:
        data_nascimento: Data no formato DD/MM/AAAA
        idade_minima: Idade mínima requerida (padrão: 18)
        
    Returns:
        bool: True se a data é válida e idade >= idade_minima
    """
    try:
        data = datetime.strptime(data_nascimento, "%d/%m/%Y")
        
        # Verifica se a data não é no futuro
        if data > datetime.now():
            return False
        
        # Cálculo preciso da idade
        hoje = datetime.now()
        idade = hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))
        
        return idade >= idade_minima
    except (ValueError, TypeError):
        return False

def valida_cpf(cpf: str) -> bool:
    """Valida o formato e os dígitos verificadores de um CPF.
    
    Args:
        cpf: Número do CPF a ser validado (com ou sem formatação)
        
    Returns:
        bool: True se o CPF é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos e não é uma sequência inválida
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Cálculo dos dígitos verificadores
    try:
        numeros = [int(digito) for digito in cpf]
        
        # Primeiro dígito verificador
        soma = sum(numeros[i] * (10 - i) for i in range(9))
        resto = 11 - (soma % 11)
        digito1 = resto if resto < 10 else 0
        
        # Segundo dígito verificador
        soma = sum(numeros[i] * (11 - i) for i in range(10))
        resto = 11 - (soma % 11)
        digito2 = resto if resto < 10 else 0
        
        # Verifica se os dígitos calculados conferem
        return numeros[9] == digito1 and numeros[10] == digito2
    except:
        return False

def formata_cpf(cpf: str) -> str:
    """Formata um CPF válido no padrão XXX.XXX.XXX-XX.
    
    Args:
        cpf: Número do CPF (com ou sem formatação)
        
    Returns:
        str: CPF formatado ou string vazia se inválido
    """
    if not valida_cpf(cpf):
        return ""
    
    cpf = re.sub(r'[^0-9]', '', cpf)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"