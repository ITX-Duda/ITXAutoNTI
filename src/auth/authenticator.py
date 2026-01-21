"""
Módulo de Template para Autenticação no GLPI.

Este módulo usa os App-Token e User-Token para iniciar uma sessão.
"""

import httpx
from src.utils.config_loader import chaves # Importa as configurações do .env!

class Authenticator:
    """
    Classe (Template) para gerenciar a autenticação e a sessão com o GLPI.
    """
    def __init__(self):
        """
        Inicializa o autenticador carregando as configurações do .env.
        """
        self.api_url = chaves.get("GLPI_API_URL")
        self.app_token = chaves.get("GLPI_APP_TOKEN")
        self.user_token = chaves.get("GLPI_USER_TOKEN")
        self.session_token = None
        self.client = None # O cliente HTTP será inicializado no login

    def init_session(self):
        """
        Usa a lógica da equipe para iniciar a sessão e obter o session_token.
        """
        # Cabeçalhos base para iniciar a sessão
        headers = {
            'App-Token': self.app_token,
            'Authorization': f'user_token {self.user_token}',
            'Content-Type': 'application/json',
        }

        try:
            response = httpx.get(f"{self.api_url}/initSession", headers=headers, verify=False)
            response.raise_for_status() # Lança um erro se a resposta for 4xx ou 5xx
            
            self.session_token = response.json().get('session_token')
            if not self.session_token:
                print("Erro: Token de sessão não recebido da API.")
                return False

            print("Autenticação bem-sucedida.")
            
            # Cria um cliente HTTP reutilizável com os cabeçalhos de sessão
            self._setup_client()
            return True
            
        except httpx.HTTPStatusError as e:
            print(f"Erro HTTP ao autenticar: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"Erro inesperado ao autenticar: {e}") 
        
        return False

    def _setup_client(self):
        """
        Cria um cliente HTTP persistente com todos os headers de autenticação.
        """
        if not self.session_token:
            return

        # Estes são os headers que serão usados em TODAS as futuras requisições
        session_headers = {
            'App-Token': self.app_token,
            'Authorization': f'user_token {self.user_token}',
            'Content-Type': 'application/json',
            'Session-Token': self.session_token
        }
        
        self.client = httpx.Client(
            base_url=self.api_url, 
            headers=session_headers, 
            verify=False
        )
        print("Cliente HTTP pronto para uso.")

    def get_client(self):
        """
        Método público para obter o cliente HTTP autenticado.
        """
        if not self.client:
            print("Erro: Cliente não inicializado. Chame init_session() primeiro.")
            return None
        return self.client

    def close_session(self):
        """
        Encerra a sessão no GLPI e fecha o cliente HTTP.
        """
        if self.client:
            try:
                self.client.get("/killSession") # Usa a base_url do cliente
                print("Sessão encerrada no GLPI.")
            except httpx.RequestError as e:
                print(f"Erro ao encerrar sessão: {e}")
            finally:
                self.client.close()
                print("Cliente HTTP fechado.")
                self.session_token = None
                self.client = None
