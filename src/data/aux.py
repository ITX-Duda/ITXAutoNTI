import requests
import urllib3
from typing import List, Dict

def find_itx_mentions_in_tasks(
    session_token: str,
    app_token: str,
    api_url: str,
    ticket_ids: list
):
    headers = {
        "Content-Type": "application/json",
        "Session-Token": session_token,
        "App-Token": app_token
    }

    keywords = ["itxautonti", "41441"]

    found = []

    for ticket_id in ticket_ids:
        print(f"\n🔎 Verificando chamado #{ticket_id}...")

        url = f"{api_url.rstrip('/')}/Ticket/{ticket_id}/TicketTask"

        try:
            resp = requests.get(url, headers=headers, verify=False)
            resp.raise_for_status()
            tasks = resp.json()
        except Exception as e:
            print(f"❌ Erro ao buscar tasks do chamado {ticket_id}: {e}")
            continue

        if not tasks:
            print("   ⛔ Nenhuma task encontrada.")
            continue

        for task in tasks:
            content = (task.get("content") or "").lower()
            task_id = task.get("id")

            if any(k in content for k in keywords):
                print("   ✅ MENÇÃO ENCONTRADA!")
                print(f"      🎫 Chamado: {ticket_id}")
                print(f"      🧩 Task ID: {task_id}")
                print(f"      📝 Conteúdo: {task.get('content')}")

                found.append({
                    "ticket_id": ticket_id,
                    "task_id": task_id,
                    "content": task.get("content")
                })

    return found
