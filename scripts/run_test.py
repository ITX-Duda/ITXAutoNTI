"""
Script de teste para executar o fluxo de autenticação e leitura de usuário.

Como executar (no PowerShell, na raiz do projeto):
(venv) > python scripts/run_test.py
"""

import sys
import os

# --- Mágica para o Python encontrar a pasta 'src' ---
# Pega o caminho do diretório atual (scripts)
current_dir = os.path.dirname(__file__)
# Sobe um nível para a pasta raiz (ITXAutoNTI)
project_root = os.path.abspath(os.path.join(current_dir, ".."))
# Adiciona a raiz ao 'caminho' do Python
sys.path.insert(0, project_root)
# ----------------------------------------------------

# Agora podemos importar de 'src'
from src.utils.config_loader import settings  # Importa os segredos do .env
from src.auth.session import autenticar_glpi  # Importa a Função 1
from src.data.reader import user_name         # Importa a Função 2

def main():
    print("--- Iniciando teste da equipe ---")
    
    # 1. Carrega os segredos do settings (que leu o .env)
    api_url = settings.get("GLPI_API_URL")
    app_token = settings.get("GLPI_APP_TOKEN")
    user_token = settings.get("GLPI_USER_TOKEN")

    if not all([api_url, app_token, user_token]):
        print("Erro: Configurações da API não encontradas no .env. Abortando.")
        return

    # 2. Executa a Função 1 (Autenticação)
    session_token = autenticar_glpi(api_url, app_token, user_token)

    # 3. Executa a Função 2 (Leitura), se a Função 1 deu certo
    if session_token:
        user_name(api_url, app_token, user_token, session_token)
    else:
        print("Não foi possível obter o nome do usuário pois a autenticação falhou.")
    
    print("--- Teste concluído ---")

# Isso garante que main() só é chamado quando executamos o script diretamente
if __name__ == "__main__":
    main()