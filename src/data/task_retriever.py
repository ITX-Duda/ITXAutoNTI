import requests
import urllib3
from typing import List, Dict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getItxTasks(sessionToken: str, appToken: str, apiUrl: str) -> List[Dict]:
    headers = {
        "Content-Type": "application/json",
        "Session-Token": sessionToken,
        "App-Token": appToken
    }

    # =========================
    # BUSCA DOS CHAMADOS
    # =========================
    urlPesquisa = f"{apiUrl.rstrip('/')}/search/Ticket"

    parametros = {
        # Chamados da CGP:
        "criteria[0][link]": "AND",
        "criteria[0][field]": "8",
        "criteria[0][searchtype]": "contains",
        "criteria[0][value]": "cgp",

        # Chamados de emprestimo:
        "criteria[1][link]": "AND",
        "criteria[1][field]": "1",
        "criteria[1][searchtype]": "contains",
        "criteria[1][value]": "Empréstimo",

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

    resp = requests.get(urlPesquisa, headers=headers, params=parametros, verify=False)
    resp.raise_for_status()

    data = resp.json()
    tickets = data.get("data", [])
    keywords = ['itxautonti', '41441']
    found = []
#DETALHE: Melhor citar ele no conteudo da task do que atribuir a ele, foi assim que fiz pelo menos
    for t in tickets: #percorre a busca dos chamados
        ticketId = t.get("2")  # Campo ID do chamado
        urlTask = f"{apiUrl.rstrip('/')}/Ticket/{ticketId}/TicketTask"
        respTask = requests.get(urlTask, headers=headers, verify=False)
        respTask.raise_for_status()

        tasks = respTask.json() or []
        encontrou = False

        for task in tasks: #buscas os ids das tasks dentro dos chamados
            taskId = task.get("id")
            content = (task.get("content") or "").lower()

            if any(k in content for k in keywords):
                encontrou = True
                found.append({
                    "ticket_id": ticketId,
                    "task_id": taskId
                })

        if not encontrou:
            print("   ❌ Nenhuma task cita o ITX")
    width = 40

    print(f"🎫 Chamado: | 🧩 Task: ".center(width))
    print("-" * width)
    for item in found:
        linha = f"{item['ticket_id']} | {item['task_id']}"
        print(linha.center(width))
    print("-" * width)
    print(f"📦 Total de chamados: {len(set(i['ticket_id'] for i in found))}".center(width))
    print(f"🍧 Total de tasks: {len(found)}".center(width))
    return found