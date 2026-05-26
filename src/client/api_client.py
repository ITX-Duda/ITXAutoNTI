import httpx
from src.utils.logger import logger

class ApiClient:
    """
    O que faz?
    Classe responsável por centralizar a comunicação de rede (HTTP) com a API do GLPI.
    Gerencia ativamente o Token de Sessão persistente (Pool TCP) e injeção de Headers, garantindo que cada requisição esteja autenticada sem precisar passar o Token manualmente.
    """
    
    def __init__(self, apiUrl: str, appToken: str, userToken: str):
        """
        O que faz?
        Inicializa o cliente com os dados de acesso vindos do .env, mas não realiza conexões ainda.

        Argumentos Necessários:
        - apiUrl (str): A URL base do GLPI
        - appToken (str): Token de liberação do aplicativo no GLPI
        - userToken (str): Token do usuário bot
        """
        self.apiUrl = apiUrl.rstrip("/")
        self.appToken = appToken
        self.userToken = userToken
        self.sessionToken = None
        self.client = None

    def initSession(self) -> bool:
        """
        O que faz?
        Aciona o endpoint de login (`/initSession`), resgata o "Session-Token" e instancia o objeto `httpx.Client` que será usado em toda a vida útil da aplicação.

        O que retorna? 
        - True (Se o login ocorreu com sucesso)
        - False (Caso falhe)
        """
        headers = {
            'App-Token': self.appToken,
            'Authorization': f'user_token {self.userToken}',
            'Content-Type': 'application/json',
        }
        try:
            response = httpx.get(f"{self.apiUrl}/initSession", headers=headers, verify=False)
            response.raise_for_status()
            
            self.sessionToken = response.json().get('session_token')
            if not self.sessionToken:
                logger.error("Token de sessão não recebido da API.")
                return False

            logger.info("Autenticacao bem-sucedida.")
            
            sessionHeaders = {
                'App-Token': self.appToken,
                'Content-Type': 'application/json',
                'Session-Token': self.sessionToken
            }
            
            self.client = httpx.Client(
                base_url=self.apiUrl, 
                headers=sessionHeaders, 
                verify=False
            )
            return True
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao autenticar: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Erro inesperado ao autenticar: {e}") 
        
        return False

    def killSession(self):
        """
        O que faz?
        Encerra educadamente a sessão logada dentro do servidor GLPI, desocupando o espaço de memória do banco de dados e encerrando as conexões HTTP locais persistentes.
        """
        if self.client:
            try:
                self.client.get("/killSession")
                logger.info("Sessão encerrada no GLPI.")
            except httpx.RequestError as e:
                logger.error(f"Erro ao encerrar sessão: {e}")
            finally:
                self.client.close()
                self.sessionToken = None
                self.client = None

    def get(self, endpoint: str, params: dict = None) -> httpx.Response:
        """
        O que faz?
        Executa uma requisição GET autenticada.

        Argumentos Necessários:
        - endpoint (str): A rota da API
        - params (dict): Parâmetros opcionais da URL

        O que retorna? 
        - A resposta raw do servidor
        """
        if not self.client:
            raise ValueError("Cliente não inicializado. Chame initSession() primeiro.")
        return self.client.get(endpoint, params=params)

    def post(self, endpoint: str, json: dict = None, data: dict = None, files: dict = None, headers: dict = None) -> httpx.Response:
        """
        O que faz?
        Executa uma requisição POST autenticada, permitindo a sobrescrita do Content-Type nativo para facilitar a realização de envio de arquivos ("multipart/form-data").

        Argumentos Necessários:
        - endpoint (str): A rota de criação
        - json/data/files/headers (opcional): Pacotes de dados injetados no corpo

        O que retorna? 
        - A resposta HTTP
        """
        if not self.client:
            raise ValueError("Cliente não inicializado. Chame initSession() primeiro.")
        
        reqHeaders = self.client.headers.copy()
        if headers:
            reqHeaders.update(headers)
            
        return self.client.post(endpoint, json=json, data=data, files=files, headers=reqHeaders)

    def put(self, endpoint: str, json: dict = None) -> httpx.Response:
        """
        O que faz?
        Executa uma requisição PUT (Update) autenticada. Utilizada para trocar Status/Locais dos itens.

        Argumentos Necessários:
        - endpoint (str): A rota de atualização
        - json (dict): O payload com os novos campos

        O que retorna? 
        - A resposta HTTP
        """
        if not self.client:
            raise ValueError("Cliente não inicializado. Chame initSession() primeiro.")
        return self.client.put(endpoint, json=json)

    def delete(self, endpoint: str) -> httpx.Response:
        """
        O que faz?
        Executa uma requisição DELETE autenticada. Utilizada para quebrar vínculos da tabela Item_Ticket.

        Argumentos Necessários:
        - endpoint (str): A rota de exclusão

        O que retorna? 
        - A resposta HTTP
        """
        if not self.client:
            raise ValueError("Cliente não inicializado. Chame initSession() primeiro.")
        return self.client.delete(endpoint)
