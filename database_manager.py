import json
from pathlib import Path
import shutil
from decimal import Decimal
from datetime import datetime, date



class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)
    
class DatabaseManager:
    """Gerencia a persistência dos dados em arquivo JSON com backup automático."""
    
    def __init__(self, file_path='database/banco_ufs.json'):
        """
        Inicializa o gerenciador de banco de dados.
        
        Args:
            file_path (str): Caminho para o arquivo JSON principal
        """
        self.file_path = Path(file_path)
        self.backup_dir = self.file_path.parent / 'backups'
        self._create_file_if_not_exists()
    
    def _create_file_if_not_exists(self):
        """Cria o arquivo JSON com estrutura inicial se não existir."""
        try:
            # Garante que o diretório existe
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Cria arquivo apenas se não existir
            if not self.file_path.exists():
                initial_data = {
                    "usuarios": [],
                    "contas": [],
                    "ultimo_numero_conta": 0,
                    "metadata": {
                        "data_criacao": datetime.now().isoformat(),
                        "versao": "1.0"
                    }
                }
                self._save_to_file(initial_data)
                
            # Garante que o diretório de backups existe
            self.backup_dir.mkdir(exist_ok=True)
                
        except Exception as e:
            raise DatabaseError(f"Falha ao inicializar arquivo de dados: {str(e)}")

    def _validate_data(self, data):
        """Valida a estrutura básica dos dados."""
        if not isinstance(data, dict):
            raise DatabaseError("Dados devem ser um dicionário")
        
        required_keys = {'usuarios', 'contas', 'ultimo_numero_conta'}
        if not required_keys.issubset(data.keys()):
            raise DatabaseError(f"Dados devem conter as chaves: {required_keys}")
        
        return True

    def _create_backup(self):
        """Cria um backup do arquivo atual com timestamp."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"banco_ufs_backup_{timestamp}.json"
            shutil.copy2(self.file_path, backup_file)
            
            backups = sorted(self.backup_dir.glob("banco_ufs_backup_*.json"))
            for old_backup in backups[:-5]:
                old_backup.unlink()
                
        except Exception as e:
            raise DatabaseError(f"Falha ao criar backup: {str(e)}")

    def _save_to_file(self, data):
        """Salva dados no arquivo com tratamento de erro."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False, cls=DecimalEncoder)
        except Exception as e:
            raise DatabaseError(f"Falha ao salvar dados: {str(e)}")

    def load_data(self):
        """
        Carrega os dados do arquivo JSON.
        
        Returns:
            dict: Dados carregados do arquivo
            
        Raises:
            DatabaseError: Se houver erro ao carregar ou validar os dados
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            self._validate_data(data)
            return data
            
        except json.JSONDecodeError as e:
            raise DatabaseError(f"Arquivo corrompido: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Falha ao carregar dados: {str(e)}")

    def save_data(self, data):
        """
        Salva dados no arquivo JSON com backup automático.
        
        Args:
            data (dict): Dados a serem salvos
            
        Raises:
            DatabaseError: Se houver erro ao validar ou salvar os dados
        """
        try:
            self._validate_data(data)
            self._create_backup()
            self._save_to_file(data)
        except Exception as e:
            # Tenta restaurar do backup em caso de erro
            try:
                backups = sorted(self.backup_dir.glob("banco_ufs_backup_*.json"))
                if backups:
                    shutil.copy2(backups[-1], self.file_path)
            except:
                pass
            raise DatabaseError(f"Erro ao salvar dados: {str(e)}")

    def get_backup_files(self):
        """Retorna lista de arquivos de backup disponíveis."""
        return sorted(self.backup_dir.glob("banco_ufs_backup_*.json"))


class DatabaseError(Exception):
    """Exceção personalizada para erros do DatabaseManager."""
    pass