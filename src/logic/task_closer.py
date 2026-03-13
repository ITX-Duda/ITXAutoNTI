# src/logic/task_closer.py


import os
import json
import httpx
from typing import Dict, Any, Optional, List

class GlpiSender:
    def __init__(self, api_url: str, app_token: str, session_token: str):
        self.api_url = api_url.rstrip("/")
        self.headers_json = {
            "App-Token": app_token,
            "Session-Token": session_token,
            "Content-Type": "application/json",
        }
        self.headers_multipart = {
            "App-Token": app_token,
            "Session-Token": session_token,
        }
        
        self.client = httpx.Client(
            base_url=self.api_url,
            headers=self.headers_json,
            verify=False,
        )

    def get_task_author_mention(self, task_id: int) -> str:
        """Busca o usuário que criou a task para fazer a menção com NOME COMPLETO."""
        try:
            # 1. Acha o ID do autor da task
            resp_task = self.client.get(f"/TicketTask/{task_id}")
            resp_task.raise_for_status()
            users_id = resp_task.json().get("users_id")
            
            if not users_id:
                return ""
                
            # 2. Pega os dados do usuário no GLPI
            resp_user = self.client.get(f"/User/{users_id}")
            resp_user.raise_for_status()
            user_data = resp_user.json()
            
            # --- MÁGICA DO NOME COMPLETO ---
            primeiro_nome = user_data.get("firstname") or ""
            sobrenome = user_data.get("realname") or ""
            
            # Junta os dois (Ex: "Paula Costa")
            nome_completo = f"{primeiro_nome} {sobrenome}".strip()
            
            # Backup: se o usuário não tiver nome preenchido, usa o login ('name')
            if not nome_completo:
                nome_completo = user_data.get("name") or "Usuário"
                
            # 3. Retorna a tag com o nome bonito!
            return f'<a class="user-mention" data-users-id="{users_id}">@{nome_completo}</a>'
            
        except Exception as e:
            print(f"⚠️ Não foi possível buscar o criador da task {task_id}: {e}")
            return ""

    def mark_task_done(self, task_id: int) -> Dict[str, Any]:
        """Fecha task original (state=2)."""
        try:
            response = self.client.put(
                f"/TicketTask/{task_id}",
                json={"input": {"state": 2}},
            )
            response.raise_for_status()
            print(f"✅ Task {task_id} fechada (Feita)")
            return {"success": True}
        except Exception as e:
            print(f"❌ Erro ao fechar task {task_id}: {e}")
            return {"success": False, "error": str(e)}

    def create_info_task(self, ticket_id: int, message: str) -> Dict[str, Any]:
        """Cria nova task de informação (state=0)."""
        try:
            payload = {
                "tickets_id": ticket_id,
                "content": message,
                "state": 0,
                "is_html": 1  # Informação
            }
            response = self.client.post(
                "/TicketTask",
                json={"input": payload},
            )
            response.raise_for_status()
            new_task_id = response.json().get("id")
            print(f"✅ Nova task de informação criada (ID: {new_task_id})")
            return {"success": True, "new_task_id": new_task_id}
        except Exception as e:
            print(f"❌ Erro ao criar task de informação: {e}")
            return {"success": False, "error": str(e)}

    def upload_document(self, itemtype: str, items_id: int, file_path: str) -> Dict[str, Any]:
        """Anexa o arquivo CSV no GLPI vinculado a um item específico (Ticket ou TicketTask)."""
        if not file_path or not os.path.exists(file_path):
            return {"success": False, "error": "Arquivo CSV não encontrado."}

        filename = os.path.basename(file_path)

        manifest = {
            "input": {
                "name": f"Histórico de Execução - {filename}",
                "_filename": [filename],
                "itemtype": itemtype,
                "items_id": items_id
            }
        }

        try:
            with open(file_path, "rb") as f:
                files = {
                    'uploadManifest': (None, json.dumps(manifest), 'application/json'),
                    'filename[0]': (filename, f, 'text/csv')
                }
                
                response = httpx.post(
                    f"{self.api_url}/Document",
                    headers=self.headers_multipart,
                    files=files,
                    verify=False
                )
                response.raise_for_status()
                
                doc_id = response.json().get("id", "unknown")
                print(f"📎 Anexo enviado com sucesso! (Doc ID: {doc_id})")
                return {"success": True, "doc_id": doc_id}
        except Exception as e:
            print(f"❌ Erro ao enviar anexo: {e}")
            return {"success": False, "error": str(e)}


def close_task(
    api_url: str,
    app_token: str,
    session_token: str,
    task_id: str,
    ticket_id: str,
    resultados: List[Any],
    csv_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fluxo completo:
    """
    if not task_id.isdigit() or not ticket_id.isdigit():
        return {"success": False, "reason": "task_id ou ticket_id inválido"}

    sender = GlpiSender(api_url, app_token, session_token)

    # 1) Descobre quem abriu a task antes de fechar ela
    mention = sender.get_task_author_mention(int(task_id))

    # 2) Fecha task original
    task_done = sender.mark_task_done(int(task_id))
    if not task_done["success"]:
        return task_done

    # 3) Monta o relatório detalhado
    sucessos = 0
    total = len(resultados)
    linhas_itens = []
    
    for r in resultados:
        # Pega as variáveis principais
        is_success = getattr(r, "success", False) or (isinstance(r, dict) and r.get("success", False))
        pat = getattr(r, "patrimonio", "") or (isinstance(r, dict) and r.get("patrimonio", ""))
        acao = (getattr(r, "action", "") or (isinstance(r, dict) and r.get("action", ""))).lower()
        erro = getattr(r, "erro", "") or (isinstance(r, dict) and r.get("erro", ""))
        lanc = getattr(r, "lancStatusamento", "") or (isinstance(r, dict) and r.get("lancStatusamento", ""))
        
        if is_success:
            sucessos += 1
            
        # Define se foi inserido ou removido
        if acao == "remover":
            acao_passado = "removido"
        elif acao == "inserir":
            acao_passado = "inserido"
        else:
            acao_passado = acao
            
        # Extrai o Status e a Localização da string
        status = "?"
        localizacao = "?"
        for parte in lanc.split("|"):
            if parte.startswith("STATUS_DEPOIS:"):
                status = parte.split(":", 1)[1]
            elif parte.startswith("LOCAL_DEPOIS:"):
                localizacao = parte.split(":", 1)[1]
        
        # MENSAGENS PERSONALIZADAS
        if is_success:
            linhas_itens.append(f"✅ {pat} foi {acao_passado}, status atual: {status} e localização: {localizacao}")
        else:
            msg_erro = erro if erro else "Erro desconhecido"
            linhas_itens.append(f"❌ {pat} não foi {acao_passado}")

    # Junta os itens quebrando linha com a tag HTML <br> para funcionar bem com a menção

    # Junta os itens usando apenas a tag HTML <br>
    texto_itens = "<br>".join(linhas_itens)

    # Mensagem final formatada 100% em HTML para o GLPI pular as linhas corretamente
    message = (
        f"{mention},<br><br>"
        f"🤝 Ohh zé, bão?<br><br>"
        f"Executada e fechada com sucesso tarefa: #{task_id}<br><br>"
        f"{sucessos}/{total} Itens tratados:<br><br>"
        f"{texto_itens}"
    )

    # 5) Nova task de informação
    info_task = sender.create_info_task(int(ticket_id), message)
    new_task_id = info_task.get("new_task_id")

    # 6) Upload do CSV
    # 6) Upload do CSV
    # 6) Upload do CSV
    doc_upload = {"success": False}
    
    # Agora exigimos que a nova task tenha sido criada para anexar nela
    if csv_file and new_task_id:
        print(f"🔎 Preparando para anexar CSV dentro da Tarefa {new_task_id}...")
        
        # Mudamos de 'Ticket' para 'TicketTask' e passamos o ID da task nova
        doc_upload = sender.upload_document(
            itemtype="TicketTask", 
            items_id=int(new_task_id), 
            file_path=csv_file
        )
        
        if doc_upload.get("success"):
            print("✅ CSV anexado com sucesso dentro da tarefa de informação!")
        else:
            print(f"❌ Falha no anexo: {doc_upload.get('error')}")

    return {
        "success": info_task.get("success", False),
        "task_done": task_done,
        "info_task": info_task,
        "document_uploaded": doc_upload
    }