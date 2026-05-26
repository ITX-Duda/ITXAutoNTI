import os
from dotenv import load_dotenv
from src.utils.logger import logger

def loadConfig():
    """
    O que faz?
    Carrega as configurações sensíveis do sistema a partir de um arquivo .env.

    O que retorna?
    - Dicionário contendo as chaves carregadas (API_URL, APP_TOKEN, USER_TOKEN)
    - Retorna None caso falte alguma chave ou o arquivo
    """
    projectRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    envPath = os.path.join(projectRoot, "config", ".env")
    
    if not os.path.exists(envPath):
        logger.warning(f"Arquivo .env não encontrado em {envPath}")
        logger.warning(f"Crie {envPath} com as chaves: GLPI_API_URL, GLPI_APP_TOKEN, GLPI_USER_TOKEN")
        return None 
    
    load_dotenv(dotenv_path=envPath)
    
    chaves = {
        "GLPI_API_URL": os.getenv("GLPI_API_URL"), 
        "GLPI_APP_TOKEN": os.getenv("GLPI_APP_TOKEN"), 
        "GLPI_USER_TOKEN": os.getenv("GLPI_USER_TOKEN")
    }
    
    if not all(chaves.values()):
        logger.warning("Uma ou mais variáveis (API_URL, APP_TOKEN, USER_TOKEN) não estão definidas no arquivo .env.")
        return None
        
    return chaves
    
chaves = loadConfig()