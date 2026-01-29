import os
from dotenv import load_dotenv

def loadConfig(): # retorna um dict

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    env_path = os.path.join(project_root, "config", ".env")
    
    if not os.path.exists(env_path): # checa se a .env existe mesmo
        print(f"AVISO: Arquivo .env não encontrado em {env_path}")
        print(f"Crie {env_path} com:")
        print("GLPI_API_URL")
        print("GLPI_APP_TOKEN")
        print("GLPI_USER_TOKEN")
        return None 
    
    load_dotenv(dotenv_path=env_path) # Carrega do arquivo
    
    chaves = {"GLPI_API_URL": os.getenv("GLPI_API_URL"), "GLPI_APP_TOKEN": os.getenv("GLPI_APP_TOKEN"), "GLPI_USER_TOKEN": os.getenv("GLPI_USER_TOKEN"),}
    
    if not all(chaves.values()): #verifica se todos os valores são truthy
        print("AVISO: Uma ou mais variáveis (API_URL, APP_TOKEN, USER_TOKEN) não estão definidas.")
        return None
    return chaves
    
chaves = loadConfig()