import os
from dotenv import load_dotenv

def load_config():
    """
    Carrega as variáveis de ambiente do arquivo .env da pasta RAIZ do projeto.
    """
    # Encontra a pasta raiz do projeto (subindo de src/utils)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    env_path = os.path.join(project_root, "config", ".env")

    if not os.path.exists(env_path):
        print(f"AVISO: Arquivo .env não encontrado em {env_path}")
        load_dotenv() # Tenta carregar do ambiente
    else:
        load_dotenv(dotenv_path=env_path) # Carrega do arquivo
    
    config = {
        "GLPI_API_URL": os.getenv("GLPI_API_URL"),
        "GLPI_APP_TOKEN": os.getenv("GLPI_APP_TOKEN"),
        "GLPI_USER_TOKEN": os.getenv("GLPI_USER_TOKEN"),
    }
    
    if not all(config.values()):
        print("AVISO: Uma ou mais variáveis (API_URL, APP_TOKEN, USER_TOKEN) não estão definidas.")
        
    return config

# Carrega as configs UMA VEZ para que outros arquivos possam importá-las
settings = load_config()