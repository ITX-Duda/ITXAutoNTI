import os
import json
import httpx
from typing import Dict, Any, Optional, List
from src.utils.logger import logger


def getTaskAuthorMention(apiClient, taskId: int) -> str:
    """
    O que faz?
    Engenharia Social/Interface. Entra nos dados do usuário que solicitou o serviço e monta o Código HTML necessário para que ele receba uma notificação (Tag) informando o término da ação.

    Argumentos Necessários:
    - apiClient (ApiClient): Rede.
    - taskId (int): ID da tarefa que está sendo processada.

    O que retorna? 
    - String HTML com a menção de nome completo do autor da tarefa original.
    """
    try:
        respTask = apiClient.get(f"/TicketTask/{taskId}")
        respTask.raise_for_status()
        usersId = respTask.json().get("users_id")
        
        if not usersId:
            return ""
            
        respUser = apiClient.get(f"/User/{usersId}")
        respUser.raise_for_status()
        userData = respUser.json()
            
        primeiroNome = userData.get("firstname") or ""
        sobrenome = userData.get("realname") or ""
        
        nomeCompleto = f"{primeiroNome} {sobrenome}".strip()
        
        if not nomeCompleto:
            nomeCompleto = userData.get("name") or "Usuário"
            
        return f'<a class="user-mention" href="/front/user.form.php?id={usersId}">@{nomeCompleto}</a>'
            
    except Exception as e:
        logger.warning(f"📢❗Não foi possível buscar o criador da task {taskId}: {e}")
        return ""

def markTaskDone(apiClient, taskId: int) -> Dict[str, Any]:
    """
    O que faz?
    Fecha e retira a tarefa primária da esteira do robô. Sem isso, o robô ficaria processando a mesma máquina eternamente num loop.

    Argumentos Necessários:
    - apiClient (ApiClient): Rede.
    - taskId (int): ID da Tarefa.

    O que retorna? 
    - Objeto de Status de sucesso ou falha da transação PUT.
    """
    try:
        response = apiClient.put(
            f"/TicketTask/{taskId}",
            json={"input": {"state": 2}},
        )
        response.raise_for_status()
        logger.info(f"✅ Task #{taskId} concluída (Fechada)")
        return {"success": True}
    except Exception as e:
        logger.error(f"🚨 Erro ao fechar task {taskId}: {e}")
        return {"success": False, "error": str(e)}

def createInfoTask(apiClient, ticketId: int, message: str) -> Dict[str, Any]:
    """
    O que faz?
    Abre um bloco de resposta automática dentro do chamado do usuário relatando o resumo da operação em HTML.

    Argumentos Necessários:
    - apiClient (ApiClient): Rede.
    - ticketId (int): ID do chamado base.
    - message (str): Mensagem finalizada e montada em HTML.

    O que retorna? 
    - Status de sucesso
    - ID dessa nova tarefa criativa gerada pelo robô
    """
    try:
        payload = {
            "tickets_id": ticketId,
            "content": message,
            "state": 0,
            "is_html": 1  
        }
        response = apiClient.post(
            "/TicketTask",
            json={"input": payload},
        )
        response.raise_for_status()
        newTaskId = response.json().get("id")
        logger.info(f"📝 Nova task de informação criada (ID: {newTaskId})")
        return {"success": True, "newTaskId": newTaskId}
    except Exception as e:
        logger.error(f"🚨 Erro ao criar task de informação: {e}")
        return {"success": False, "error": str(e)}

def uploadDocument(apiClient, itemType: str, itemsId: int, filePath: str) -> Dict[str, Any]:
    """
    O que faz?
    Protocolo de Upload Assíncrono (Multipart/Form-data). Converte o arquivo físico CSV gerado pela auditoria e o "sobe" no sistema do GLPI em anexo dentro da caixa de resposta.

    Argumentos Necessários:
    - apiClient (ApiClient): Rede.
    - itemType (str): Aonde anexar (Sempre "TicketTask").
    - itemsId (int): O local do anexo.
    - filePath (str): Caminho local do CSV salvo pela máquina.

    O que retorna? 
    - Status de sucesso
    - ID interno do documento registrado no servidor do GLPI
    """
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
            files = {'uploadManifest': (None, json.dumps(manifest), 'application/json'), 'filename[0]': (fileName, f, 'text/csv')}
            
            headersMultipart = {
                "App-Token": apiClient.appToken,
                "Session-Token": apiClient.sessionToken,
            }
            
            response = httpx.post(
                f"{apiClient.apiUrl}/Document",
                headers=headersMultipart,
                files=files,
                verify=False
            )
            response.raise_for_status()
            
            docId = response.json().get("id", "unknown")
            return {"success": True, "docId": docId}
    except Exception as e:
        logger.error(f"🚨 Erro ao enviar anexo: {e}")
        return {"success": False, "error": str(e)}


def closeTask(apiClient, taskId: str, ticketId: str, resultados: List[Any], csvFile: Optional[str] = None) -> Dict[str, Any]:
    """
    O que faz?
    Função Master que agrupa e coordena o fluxo de encerramento de tarefas no sistema simulando passos de técnico.

    Argumentos Necessários:
    - apiClient (ApiClient): Rede.
    - taskId (str): ID da tarefa primária.
    - ticketId (str): ID do chamado base.
    - resultados (List[Any]): A lista de objetos contendo os históricos da operação.
    - csvFile (Optional[str]): O caminho absoluto para o anexo CSV.

    O que retorna? 
    - Dicionário super completo agrupando sucesso das instâncias de fechar, criar tarefa informativa e subir documento.
    """
    if not taskId.isdigit() or not ticketId.isdigit():
        return {"success": False, "reason": "taskId ou ticketId inválido"}

    mention = getTaskAuthorMention(apiClient, int(taskId))

    taskDone = markTaskDone(apiClient, int(taskId))
    if not taskDone["success"]:
        return taskDone

    sucessos = 0
    total = len(resultados)
    linhasItens = []
    
    for r in resultados:
        isSuccess = getattr(r, "success", False) or (isinstance(r, dict) and r.get("success", False))
        pat = getattr(r, "patrimonio", "") or (isinstance(r, dict) and r.get("patrimonio", ""))
        acao = (getattr(r, "action", "") or (isinstance(r, dict) and r.get("action", ""))).lower()
        erro = getattr(r, "erro", "") or (isinstance(r, dict) and r.get("erro", ""))
        lanc = getattr(r, "lancStatusamento", "") or (isinstance(r, dict) and r.get("lancStatusamento", ""))
        
        if isSuccess:
            sucessos += 1
            
        if acao == "remover":
            acaoPassado = "removido"
        elif acao == "inserir":
            acaoPassado = "inserido"
        else:
            acaoPassado = acao
            
        statusAntes = "?"
        statusDepois = "?"
        localAntes = "?"
        localDepois = "?"
        for parte in lanc.split("|"):
            if parte.startswith("STATUS_ANTES:"):
                statusAntes = parte.split(":", 1)[1].strip()
            elif parte.startswith("STATUS_DEPOIS:"):
                statusDepois = parte.split(":", 1)[1].strip()
            elif parte.startswith("LOCAL_ANTES:"):
                localAntes = parte.split(":", 1)[1].strip()
            elif parte.startswith("LOCAL_DEPOIS:"):
                localDepois = parte.split(":", 1)[1].strip()
                
        if statusAntes == statusDepois or statusDepois == "?":
            statusDepois = "Não alterado"
            
        if localAntes == localDepois or localDepois == "?":
            localDepois = "Não alterado"
        
        if isSuccess:
            linhasItens.append(f"✅ {pat} foi {acaoPassado} >> 📊 Status: {statusDepois} >> 📍 Localização: {localDepois}")
        else:
            msgErro = erro if erro else "⚠️ Erro desconhecido"
            linhasItens.append(f"❌ {pat} não foi {acaoPassado}.{msgErro}")

    textoItens = "<br>".join(linhasItens)

    message = (
        f"{mention},<br><br>"
        f"🤝 Ocê tá bão?<br><br>"
        f"Tarefa #{taskId} finalizada com sucesso, viu!<br><br>"
        f"{sucessos}/{total} Itens tratados:<br><br>"
        f"{textoItens}"
        f"<br><br>"
        f"<small><i>*Mensagem gerada automaticamente via automação</i></small><br><br>"
    )

    infoTask = createInfoTask(apiClient, int(ticketId), message)
    newTaskId = infoTask.get("newTaskId")

    docUpload = {"success": False}
    
    if csvFile and newTaskId:       
        docUpload = uploadDocument(
            apiClient,
            itemType="TicketTask", 
            itemsId=int(newTaskId), 
            filePath=csvFile
        )
        
        if docUpload.get("success"):
            logger.info("🔗 CSV anexado.")
        else:
            logger.error(f"⚠️ Erro! Falha no anexo: {docUpload.get('error')}")

    return {
        "success": infoTask.get("success", False),
        "taskDone": taskDone,
        "infoTask": infoTask,
        "documentUploaded": docUpload
    }