import re
from bs4 import BeautifulSoup
from typing import List, Dict
from collections import defaultdict

from src.utils.logger import logger

def getItxTasks(apiClient) -> List[Dict]:
    """
    O que faz?
    Atua como um radar varrendo ativamente o banco de dados do GLPI via API para buscar tarefas alocadas à automação.

    Argumentos Necessários:
    - apiClient (ApiClient): A instância do cliente HTTP da rede.

    O que retorna? 
    - Lista de dicionários contendo os dados brutos de todas as tarefas encontradas
    """
    urlPesquisa = "/search/Ticket"
    
    parametrosPesquisa = {
        "criteria[2][link]": "AND",

        "criteria[2][criteria][0][link]": "AND",
        "criteria[2][criteria][0][field]": "12",
        "criteria[2][criteria][0][searchtype]": "equals",
        "criteria[2][criteria][0][value]": "1", 

        "criteria[2][criteria][1][link]": "OR",
        "criteria[2][criteria][1][field]": "12",
        "criteria[2][criteria][1][searchtype]": "equals",
        "criteria[2][criteria][1][value]": "2", 

        "criteria[2][criteria][2][link]": "OR",
        "criteria[2][criteria][2][field]": "12",
        "criteria[2][criteria][2][searchtype]": "equals",
        "criteria[2][criteria][2][value]": "3", 

        "criteria[2][criteria][3][link]": "OR",
        "criteria[2][criteria][3][field]": "12",
        "criteria[2][criteria][3][searchtype]": "equals",
        "criteria[2][criteria][3][value]": "4", 

        "criteria[3][link]": "AND",
        "criteria[3][field]": "26",
        "criteria[3][searchtype]": "contains",
        "criteria[3][value]": "itxautonti",
    }

    tickets = []
    ticketsBegin = 0
    ticketsLimit = 50

    while True:
        ticketsEnd = ticketsBegin + ticketsLimit - 1
        parametrosPesquisa["range"] = f"{ticketsBegin}-{ticketsEnd}"

        try:
            resp = apiClient.get(urlPesquisa, params=parametrosPesquisa)
            resp.raise_for_status()

            data = resp.json()
            ticketsPage = data.get("data", []) if data else []
            
            if not ticketsPage:
                break

            tickets.extend(ticketsPage)
            contentRange = resp.headers.get("Content-Range", "")
            
            if contentRange:
                totalMatch = int(contentRange.split("/")[-1])
                if len(tickets) >= totalMatch:
                    break
            else:
                break
        
        except Exception as e:
                logger.error(f"Erro ao buscar chamados: {e}")
                return None

        ticketsBegin += ticketsLimit

    statusMap = {
        "1": "Aberto",
        "2": "Em andamento",
        "3": "Em atendimento",
        "4": "Pendente",
        "5": "Solucionado",
        "6": "Fechado"
    }

    statusCheckbox = {
        "0": "Informação",
        "1": "A fazer", 
        "2": "Feito"
    }

    keywords = ['itxautonti', '41441']
    foundTasks = []
    doneTasksLog = []

    for ticket in tickets:
        ticketId = ticket.get("2")
        ticketStatusId = ticket.get("12")
        ticketStatusName = statusMap.get(str(ticketStatusId), "Desconhecido")

        taskUrl = f"/Ticket/{ticketId}/TicketTask"
        tasks = []
        tasksBegin = 0
        tasksLimit = 50
        
        while True:
            tasksEnd = tasksBegin + tasksLimit - 1
            parametrosTasks = {"range": f"{tasksBegin}-{tasksEnd}"}

            try:
                taskResponse = apiClient.get(taskUrl, params=parametrosTasks)
                taskResponse.raise_for_status()
                tasksPage = taskResponse.json() or []
                
                if not tasksPage:
                    break

                tasks.extend(tasksPage)
                contentRange = taskResponse.headers.get("Content-Range", "")
                if contentRange:
                    totalMatch = int(contentRange.split("/")[-1])
                    if len(tasks) >= totalMatch:
                        break
                else:
                    break

            except Exception as e:
                logger.error(f"Erro ao buscar tasks do chamado {ticketId}: {e}")
                break

            tasksBegin += tasksLimit

        hasItxTask = False

        for task in tasks:
            taskId = task.get("id")
            rawContent = task.get("content") or ""
            contentLower = rawContent.lower()
            
            taskState = task.get("state")
            stateLabel = statusCheckbox.get(str(taskState), "Desconhecido")

            if any(keyword in contentLower for keyword in keywords):
                hasItxTask = True

                if taskState == 1:
                    foundTasks.append({
                        "ticketId": ticketId,
                        "taskId": taskId,
                        "ticketStatus": ticketStatusName,
                        "state": taskState,
                        "stateLabel": stateLabel,
                        "content": rawContent, 
                        "taskState": "A fazer"
                    })

                elif taskState == 2:
                    doneTasksLog.append({
                        "ticketId": ticketId,
                        "taskId": taskId,
                        "ticketStatus": ticketStatusName,
                        "state": taskState,
                        "stateLabel": stateLabel,
                    })

        if not hasItxTask:
            logger.info(f"Nenhuma task cita o ITX no chamado {ticketId}")

    chamadosCount = len(set(t['ticketId'] for t in foundTasks))
    taskCount = len(foundTasks)
    logger.info(f"Encontrados {chamadosCount} chamados e {taskCount} tasks pendentes.")

    return foundTasks