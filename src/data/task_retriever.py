import requests
import urllib3
import re
import html
from bs4 import BeautifulSoup
from typing import List, Dict
from collections import defaultdict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def pegaTarefas(sessionToken: str, appToken: str, apiUrl: str) -> List[Dict]:
    headers = {
        "Content-Type": "application/json",
        "Session-Token": sessionToken,
        "App-Token": appToken
    }

# =========================================================================
# BUSCA DOS CHAMADOS
# =============================================================================
    urlPesquisa = f"{apiUrl.rstrip('/')}/search/Ticket"
    parametrosPesquisa = {
        # Chamados da CGP:
        """
        "criteria[0][link]": "AND",
        "criteria[0][field]": "8",
        "criteria[0][searchtype]": "contains",
        "criteria[0][value]": "cgp",
        """

        # Status: Aberto, Em andamento, Em atendimento, Pendente:
        "criteria[2][link]": "AND",

        "criteria[2][criteria][0][link]": "AND",
        "criteria[2][criteria][0][field]": "12",
        "criteria[2][criteria][0][searchtype]": "equals",
        "criteria[2][criteria][0][value]": "1", #aberto

        "criteria[2][criteria][1][link]": "OR",
        "criteria[2][criteria][1][field]": "12",
        "criteria[2][criteria][1][searchtype]": "equals",
        "criteria[2][criteria][1][value]": "2", #em andamento

        "criteria[2][criteria][2][link]": "OR",
        "criteria[2][criteria][2][field]": "12",
        "criteria[2][criteria][2][searchtype]": "equals",
        "criteria[2][criteria][2][value]": "3", #em atendimento

        "criteria[2][criteria][3][link]": "OR",
        "criteria[2][criteria][3][field]": "12",
        "criteria[2][criteria][3][searchtype]": "equals",
        "criteria[2][criteria][3][value]": "4", #pendente

        # Apenas chamados que citem o ITXAutoNTI na task:
        "criteria[3][link]": "AND",
        "criteria[3][field]": "26",
        "criteria[3][searchtype]": "contains",
        "criteria[3][value]": "itxautonti",
    }

    resp = requests.get(urlPesquisa, headers=headers, params=parametrosPesquisa, verify=False)
    resp.raise_for_status()
    data = resp.json()
    tickets = data.get("data", [])

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

        taskUrl = f"{apiUrl.rstrip('/')}/Ticket/{ticketId}/TicketTask"
        taskResponse = requests.get(taskUrl, headers=headers, verify=False)
        taskResponse.raise_for_status()
        tasks = taskResponse.json() or []

        hasItxTask = False

        for task in tasks:
            taskId = task.get("id")
            rawContent = task.get("content") or ""
            contentLower = rawContent.lower()
            taskState = task.get("state")
            stateLabel = statusCheckbox.get(str(taskState), "Desconhecido")

            if any(keyword in contentLower for keyword in keywords):
                hasItxTask = True

                if taskState == 1:  # A fazer
                    foundTasks.append({
                        "ticketId": ticketId,
                        "taskId": taskId,
                        "ticketStatus": ticketStatusName,
                        "state": taskState,
                        "stateLabel": stateLabel,
                        "content": rawContent,
                        "taskState": "A fazer"
                    })

                elif taskState == 2:  # Feito
                    doneTasksLog.append({
                        "ticketId": ticketId,
                        "taskId": taskId,
                        "ticketStatus": ticketStatusName,
                        "state": taskState,
                        "stateLabel": stateLabel,
                    })

        if not hasItxTask:
            print(" ❌ Nenhuma task cita o ITX")

    widths = [12, 10, 14]
    totalWidth = 60
    separator_width = sum(widths) + 6  # 12+10+14+6=42

    header = (
        f"{'🧩 Task':^{widths[0]}}│"
        f"{'🎫 Chamado':^{widths[1]}}│"
        f"{'⌛ Status':^{widths[2]}}"
    )
    print(header.center(totalWidth))

    separator_str = "─" * separator_width
    print(separator_str.center(totalWidth))
    for task in foundTasks:
        line = (
            f"{str(task['taskId']):>10}│"
            f"{str(task['ticketId']):>8}│"
            f"{task['taskState']:<12}"
        )
        print(line.center(totalWidth))

    print(separator_str.center(totalWidth))

    chamados = len(set(t['ticketId'] for t in foundTasks))
    tasks = len(foundTasks)
    print(f"📦 Chamados: {chamados} │ 🍧 Tasks: {tasks}".center(totalWidth))


    return foundTasks