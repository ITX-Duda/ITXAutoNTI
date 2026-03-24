# src/logic/task_closer.py

import os
import json
import httpx
from typing import Dict, Any, Optional, List

class GlpiSender:
    def __init__(self, apiUrl: str, appToken: str, sessionToken: str):
        self.apiUrl = apiUrl.rstrip("/")
        self.headersJson = {
            "App-Token": appToken,
            "Session-Token": sessionToken,
            "Content-Type": "application/json",
        }
        self.headersMultipart = {
            "App-Token": appToken,
            "Session-Token": sessionToken,
        }
        
        self.client = httpx.Client(
            base_url=self.apiUrl,
            headers=self.headersJson,
            verify=False,
        )

    def getTaskAuthorMention(self, taskId: int) -> str:
        """Busca o usuário que criou a task para fazer a menção com NOME COMPLETO."""
        try:
            # 1. Acha o ID do autor da task
            respTask = self.client.get(f"/TicketTask/{taskId}")
            respTask.raise_for_status()
            usersId = respTask.json().get("users_id")
            
            if not usersId:
                return ""
                
            # 2. Pega os dados do usuário no GLPI
            respUser = self.client.get(f"/User/{usersId}")
            respUser.raise_for_status()
            userData = respUser.json()
            
            # --- MÁGICA DO NOME COMPLETO ---
            primeiroNome = userData.get("firstname") or ""
            sobrenome = userData.get("realname") or ""
            
            # Junta os dois (Ex: "Paula Costa")
            nomeCompleto = f"{primeiroNome} {sobrenome}".strip()
            
            # Backup: se o usuário não tiver nome preenchido, usa o login ('name')
            if not nomeCompleto:
                nomeCompleto = userData.get("name") or "Usuário"
                
            # 3. Retorna a tag com o nome bonito!
            return f'<a class="user-mention" data-users-id="{usersId}">@{nomeCompleto}</a>'
            
        except Exception as e:
            print(f"⚠️ Não foi possível buscar o criador da task {taskId}: {e}")
            return ""

    def markTaskDone(self, taskId: int) -> Dict[str, Any]:
        """Fecha task original (state=2)."""
        try:
            response = self.client.put(
                f"/TicketTask/{taskId}",
                json={"input": {"state": 2}},
            )
            response.raise_for_status()
            print(f"✅ Task {taskId} fechada (Feita)")
            return {"success": True}
        except Exception as e:
            print(f"❌ Erro ao fechar task {taskId}: {e}")
            return {"success": False, "error": str(e)}

    def createInfoTask(self, ticketId: int, message: str) -> Dict[str, Any]:
        """Cria nova task de informação (state=0)."""
        try:
            payload = {
                "tickets_id": ticketId,
                "content": message,
                "state": 0,
                "is_html": 1  # Informação
            }
            response = self.client.post(
                "/TicketTask",
                json={"input": payload},
            )
            response.raise_for_status()
            newTaskId = response.json().get("id")
            print(f"✅ Nova task de informação criada (ID: {newTaskId})")
            return {"success": True, "newTaskId": newTaskId}
        except Exception as e:
            print(f"❌ Erro ao criar task de informação: {e}")
            return {"success": False, "error": str(e)}

    def uploadDocument(self, itemType: str, itemsId: int, filePath: str) -> Dict[str, Any]:
        """Anexa o arquivo CSV no GLPI vinculado a um item específico (Ticket ou TicketTask)."""
        if not filePath or not os.path.exists(filePath):
            return {"success": False, "error": "Arquivo CSV não encontrado."}

        fileName = os.path.basename(filePath)

        manifest = {
            "input": {
                "name": f"Histórico de Execução - {fileName}",
                "_filename": [fileName],
                "itemtype": itemType,
                "items_id": itemsId
            }
        }

        try:
            with open(filePath, "rb") as f:
                files = {
                    'uploadManifest': (None, json.dumps(manifest), 'application/json'),
                    'filename[0]': (fileName, f, 'text/csv')
                }
                
                response = httpx.post(
                    f"{self.apiUrl}/Document",
                    headers=self.headersMultipart,
                    files=files,
                    verify=False
                )
                response.raise_for_status()
                
                docId = response.json().get("id", "unknown")
                print(f"📎 Anexo enviado com sucesso! (Doc ID: {docId})")
                return {"success": True, "docId": docId}
        except Exception as e:
            print(f"❌ Erro ao enviar anexo: {e}")
            return {"success": False, "error": str(e)}


def closeTask(
    apiUrl: str,
    appToken: str,
    sessionToken: str,
    taskId: str,
    ticketId: str,
    resultados: List[Any],
    csvFile: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fluxo completo de fechamento de tarefa e envio de evidências.
    """
    if not taskId.isdigit() or not ticketId.isdigit():
        return {"success": False, "reason": "taskId ou ticketId inválido"}

    sender = GlpiSender(apiUrl, appToken, sessionToken)

    # 1) Descobre quem abriu a task antes de fechar ela
    mention = sender.getTaskAuthorMention(int(taskId))

    # 2) Fecha task original
    taskDone = sender.markTaskDone(int(taskId))
    if not taskDone["success"]:
        return taskDone

    # 3) Monta o relatório detalhado
    sucessos = 0
    total = len(resultados)
    linhasItens = []
    
    for r in resultados:
        # Pega as variáveis principais
        isSuccess = getattr(r, "success", False) or (isinstance(r, dict) and r.get("success", False))
        pat = getattr(r, "patrimonio", "") or (isinstance(r, dict) and r.get("patrimonio", ""))
        acao = (getattr(r, "action", "") or (isinstance(r, dict) and r.get("action", ""))).lower()
        erro = getattr(r, "erro", "") or (isinstance(r, dict) and r.get("erro", ""))
        lanc = getattr(r, "lancStatusamento", "") or (isinstance(r, dict) and r.get("lancStatusamento", ""))
        
        if isSuccess:
            sucessos += 1
            
        # Define se foi inserido ou removido
        if acao == "remover":
            acaoPassado = "removido"
        elif acao == "inserir":
            acaoPassado = "inserido"
        else:
            acaoPassado = acao
            
        # Extrai o Status e a Localização da string
        status = "?"
        localizacao = "?"
        for parte in lanc.split("|"):
            if parte.startswith("STATUS_DEPOIS:"):
                status = parte.split(":", 1)[1]
            elif parte.startswith("LOCAL_DEPOIS:"):
                localizacao = parte.split(":", 1)[1]
        
        # MENSAGENS PERSONALIZADAS
        if isSuccess:
            linhasItens.append(f"✅ {pat} foi {acaoPassado}, 📊 Status atual: {status} e 📍 Localização: {localizacao}")
        else:
            msgErro = erro if erro else "Erro desconhecido"
            linhasItens.append(f"❌ {pat} não foi {acaoPassado}.{msgErro}")

    # Junta os itens usando apenas a tag HTML <br>
    textoItens = "<br>".join(linhasItens)

    # Mensagem final formatada 100% em HTML para o GLPI pular as linhas corretamente
    message = (
        f"{mention},<br><br>"
        f"🤝 E ai meu chapa?<br><br>"
        f"Executada e fechada com sucesso tarefa: #{taskId}<br><br>"
        f"{sucessos}/{total} Itens tratados:<br><br>"
        f"{textoItens}"
    )

    # 5) Nova task de informação
    infoTask = sender.createInfoTask(int(ticketId), message)
    newTaskId = infoTask.get("newTaskId")

    # 6) Upload do CSV
    docUpload = {"success": False}
    
    # Agora exigimos que a nova task tenha sido criada para anexar nela
    if csvFile and newTaskId:
        print(f"🔎 Preparando para anexar CSV dentro da Tarefa {newTaskId}...")
        
        docUpload = sender.uploadDocument(
            itemType="TicketTask", 
            itemsId=int(newTaskId), 
            filePath=csvFile
        )
        
        if docUpload.get("success"):
            print("✅ CSV anexado com sucesso dentro da tarefa de informação!")
        else:
            print(f"❌ Falha no anexo: {docUpload.get('error')}")

    return {
        "success": infoTask.get("success", False),
        "taskDone": taskDone,
        "infoTask": infoTask,
        "documentUploaded": docUpload
    }