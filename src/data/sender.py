"""
Módulo de Template para Envio e Atualização (POST/PUT) de dados no GLPI.
"""

import httpx

class GlpiSender:
    """
    Classe (Template) para enviar e atualizar dados no GLPI.
    Requer um cliente HTTP autenticado para funcionar.
    """
    def __init__(self, client: httpx.Client):
        """
        Inicializa o enviador com um cliente HTTP já autenticado.
        
        Args:
            client (httpx.Client): O cliente vindo do Authenticator.
        """
        if not client:
            raise ValueError("O GlpiSender precisa de um cliente HTTP autenticado.")
        self.client = client

    def create_item(self, endpoint: str, payload: dict):
        """
        Cria um novo item no GLPI (ex: um Followup num Ticket).
        Usa o método POST.

        Args:
            endpoint (str): O endpoint da API (ex: "/Ticket/123/ITILFollowup")
            payload (dict): Os dados a serem enviados.
        
        Returns:
            dict: A resposta da API (geralmente o item criado), ou None se falhar.
        """
        try:
            # A API do GLPI quase sempre espera um "input" no payload
            formatted_payload = {"input": payload}
            
            # O self.client já tem a URL base e os headers de autenticação
            response = self.client.post(endpoint, json=formatted_payload)
            
            response.raise_for_status() # Lança um erro se for 4xx ou 5xx
            
            print(f"Item criado com sucesso em '{endpoint}'.")
            return response.json()

        except httpx.HTTPStatusError as e:
            print(f"Erro HTTP ao criar item em '{endpoint}': {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"Erro inesperado ao criar item: {e}")
            
        return None

    def update_item(self, endpoint: str, item_id: int, payload: dict):
        """
        Atualiza um item existente no GLPI (ex: um Ticket).
        Usa o método PUT (que o GLPI usa para 'dbUpdates').

        Args:
            endpoint (str): O tipo de item (ex: "/Ticket")
            item_id (int): O ID do item a ser atualizado.
            payload (dict): Os dados a serem atualizados.

        Returns:
            dict: A resposta da API, ou None se falhar.
        """
        try:
            full_endpoint = f"/{endpoint.strip('/')}/{item_id}"
            
            # A API do GLPI quase sempre espera um "input" no payload
            formatted_payload = {"input": payload}
            
            response = self.client.put(full_endpoint, json=formatted_payload)
            response.raise_for_status()
            
            print(f"Item {item_id} em '{endpoint}' atualizado com sucesso.")
            return response.json()

        except httpx.HTTPStatusError as e:
            print(f"Erro HTTP ao atualizar {item_id}: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"Erro inesperado ao atualizar {item_id}: {e}")
            
        return None