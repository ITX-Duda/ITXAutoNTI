import sys
import os

currentDir = os.path.dirname(__file__)
projectRoot = os.path.abspath(os.path.join(currentDir, ".."))
sys.path.insert(0, projectRoot)

from src.utils.config_loader import chaves
from src.utils.logger import logger
from src.client.api_client import ApiClient
from src.logic.task_parser import parseTaskInstruction, Instruction
from src.data.task_retriever import getItxTasks
from src.logic.task_executor import executeFromParsedTask
from src.logic.task_closer import closeTask

def main():
    """
    O que faz?
    Coordena do zero todo o ciclo de vida do software: 
        1) Login e Validação de Credenciais;
        2) Escaneamento de Demandas;
        3) Tradução Algorítmica;
        4) Operações de Banco de Dados;
        5) Encerramento e Auditoria.

    O que retorna? 
    - 0 para sucesso de execução
    - 1 para falha de execução
    """
    logger.info("Iniciando operacao.")
    logger.info("ITXAutoNTI v1.1.0")
    logger.info("Conectando ao GLPI")
    
    if not chaves:
        logger.error("Erro critico nas variaveis de ambiente (.env). Sistema interrompido.")
        return 1

    apiUrl = chaves.get("GLPI_API_URL")
    appToken = chaves.get("GLPI_APP_TOKEN")
    userToken = chaves.get("GLPI_USER_TOKEN")

    if not all([apiUrl, appToken, userToken]):
        logger.error("Credenciais insuficientes no config_loader. Abortando.")
        return 1

    apiClient = ApiClient(apiUrl, appToken, userToken)
    
    if not apiClient.initSession():
        logger.error("Falha no initSession (Autenticacao nao concluida).")
        return 1
    
    tasksEncontradas = getItxTasks(apiClient)

    if not tasksEncontradas:
        logger.info("Nenhuma task nova.")
        apiClient.killSession()
        return 0

    logger.info("Executando Tarefas")

    for idx, t in enumerate(tasksEncontradas, 1):
        ticketId = t.get("ticketId")
        taskId = t.get("taskId")
        
        logger.info(f"Chamado: #{ticketId} e Task: #{taskId} -> Em processamento.")

        instructions = parseTaskInstruction(t, apiClient)

        if not instructions:
            logger.warning(f"Task #{taskId} do chamado #{ticketId} falhou no parse ou retornou vazio.")
            continue

        results, csvFile = executeFromParsedTask(apiClient, instructions)

        resClose = closeTask(
            apiClient=apiClient,
            taskId=str(taskId),
            ticketId=str(ticketId),
            resultados=results,
            csvFile=csvFile
        )

        if resClose.get("success"):
            logger.info(f"Task fechada: #{taskId}.")
        else:
            logger.error(f"Erro ao fechar ou subir anexo: {resClose}")
    
    apiClient.killSession()
    return 0

if __name__ == "__main__":
    exit(main())