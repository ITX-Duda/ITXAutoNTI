import csv
import os
import tempfile
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from src.logic.task_parser import Instruction
from src.utils.logger import logger

def getStatusELocalItem(apiClient, itemType: str, itemId: str) -> tuple[str, str]:
    """
    O que faz?
    Procura dentro do GLPI as informações ANTERIOR do equipamento para criar um registro comparativo de histórico. 
    Força o uso do dropdown da API para captar o texto legível.

    Argumentos Necessários:
    - apiClient (ApiClient): O cliente HTTP de rede.
    - itemType (str): Tipo traduzido (ex: "Computer").
    - itemId (str): ID do equipamento.

    O que retorna? 
    - Status Anterior
    - Localização Anterior
    """
    url = f"/{itemType}/{itemId}"
    params = {"expand_dropdowns": "true"}
    
    try:
        resp = apiClient.get(url, params=params)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Erro em getStatusELocalItem: {e}")
        return f"ERRO", "N/A"

    data = resp.json()
    statusName = str(data.get("states_id") or data.get("status") or "?")
    localName = str(data.get("locations_id") or data.get("location") or "?")
    
    return statusName, localName

@dataclass
class Result:
    """
    O que faz?
    Armazena o resultado de uma transação finalizada. 
    Essa DataClass contém as métricas exatas do que mudou para ser escrito fisicamente na planilha de auditoria.
    """
    success: bool
    patrimonio: str
    itemId: str
    chamadoId: str
    tarefaId: str
    tipoItem: str
    lancStatusamento: str  
    action: str
    erro: Optional[str] = None
    already_done: bool = False

    def __str__(self) -> str:
        return (
            f"Result(success={self.success}, patrimonio={self.patrimonio}, "
            f"status={self.lancStatusamento})"
        )

def getLocationIdByCode(apiClient, codigo: str, nome: str) -> str:
    """
    O que faz?
    Decodifica os valores do Módulo Fuzzy. 
    Dado um local corrigido, descobre qual é o ID Interno desse local no banco de dados do GLPI.

    Argumentos Necessários:
    - apiClient (ApiClient): Rede.
    - codigo (str): Código do local.
    - nome (str): Nome por extenso do local.

    O que retorna? 
    - ID interno da localização
    """
    url = f"/search/Location"
    tentativas = [codigo, nome, nome.replace(" - ", " > "), nome.replace("-", " > ")]
    
    for termo in tentativas:
        if not termo: continue
        
        for field in ["1", "200"]:
            params = {
                "criteria[0][field]": field,
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": termo,
                "forcedisplay[0]": "2" 
            }
            try:
                resp = apiClient.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()

                if data.get("data") and len(data["data"]) > 0:
                    idInterno = str(data["data"][0].get("2"))
                    if idInterno and idInterno != "None":
                        return idInterno
            except Exception as e:
                logger.warning(f"Erro em getLocationIdByCode termo {termo}: {e}")
                continue
    palavra_chave = nome.split("-")[-1].strip()
    if palavra_chave:
        params_sobrevivencia = {
            "criteria[0][field]": "1",
            "criteria[0][searchtype]": "contains",
            "criteria[0][value]": palavra_chave,
            "forcedisplay[0]": "2"
        }
        try:
            resp = apiClient.get(url, params=params_sobrevivencia)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("data") and len(data["data"]) > 0:
                    idInterno = str(data["data"][0].get("2"))
                    if idInterno and idInterno != "None":
                        return idInterno
        except Exception:
            pass
    return None

def getEstadoAtualItem(apiClient, itemType: str, itemId: int) -> str:
    """
    O que faz?
    Captura o status cru numérico do item diretamente (sem forçar o expansor dropdown), usado apenas para debug ou rotinas estritas em falha do getStatusELocalItem.

    Argumentos Necessários:
    - apiClient (ApiClient): Rede.
    - itemType (str): Tipo traduzido do equipamento.
    - itemId (int): ID do equipamento.

    O que retorna? 
    - String no formato "NomeDoStatus (ID:x)".
    """
    url = f"/{itemType}/{itemId}"
    try:
        resp = apiClient.get(url)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Erro ao buscar estado atual: {e}")
        return f"ERRO_GET"

    data = resp.json()
    stateId = data.get("statusId") or "?"
    stateName = data.get("statusId_name") or "?"
    return f"{stateName} (ID:{stateId})"


def gerarHistoricoCsv(results: List[Result], chamadoId: str, tarefaId: str) -> str:
    """
    O que faz?
    Motor de conformidade financeira e operacional. Compila todos os Resultados em um arquivo CSV para fins de prestação de contas.

    Argumentos Necessários:
    - results (List[Result]): Pacote com todas as mutações realizadas.
    - chamadoId (str): ID do chamado base.
    - tarefaId (str): ID da tarefa operada.

    O que retorna? 
    - Caminho absoluto na máquina de onde o CSV foi salvo para ser upado.
    """
    reportsDir = tempfile.gettempdir()
    
    fileName = f"historico_chamado_{chamadoId}_task_{tarefaId}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filePath = os.path.join(reportsDir, fileName)

    with open(filePath, "w", newline="", encoding="utf-8") as csvFileObj:
        writer = csv.writer(csvFileObj)

        writer.writerow(
            [
                "Patrimônio",
                "Item ID",
                "Tipo",
                "Ação Solicitada",
                "Status Anterior",
                "Status Atual",
                "Localização Anterior",
                "Localização Depois",
                "Sucesso",
                "Erro (se houver)",
            ]
        )

        for result in results:
            statusAntes = ""
            statusDepois = ""
            localAntes = ""
            localDepois = ""

            parts = result.lancStatusamento.split("|")
            for part in parts:
                if part.startswith("STATUS_ANTES:"):
                    statusAntes = part.split(":", 1)[1].strip()
                elif part.startswith("STATUS_DEPOIS:"):
                    statusDepois = part.split(":", 1)[1].strip()
                elif part.startswith("LOCAL_ANTES:"):
                    localAntes = part.split(":", 1)[1].strip()
                elif part.startswith("LOCAL_DEPOIS:"):
                    localDepois = part.split(":", 1)[1].strip()

            if statusAntes == statusDepois or statusDepois == "?":
                statusDepois = "Não alterado"
            if localAntes == localDepois or localDepois == "?":
                localDepois = "Não alterado"

            writer.writerow(
                [
                    result.patrimonio,              
                    result.itemId,                  
                    result.tipoItem,                
                    result.action.upper(),          
                    statusAntes,                    
                    statusDepois,                   
                    localAntes,                     
                    localDepois,                    
                    "OK" if result.success else "FALHOU",
                    result.erro or "",
                ]
            )
    return filePath


def associarItemAoChamado(apiClient, instruction: Instruction) -> str:
    """
    O que faz?
    Cria uma nova relação de Banco de Dados entre Ativo e Ticket. Acessa a tabela oculta `Item_Ticket` e injeta o equipamento.

    Argumentos Necessários:
    - apiClient (ApiClient): Rede.
    - instruction (Instruction): Objeto contendo os IDs do Chamado e do Ativo.

    O que retorna? 
    - String sintética com Código HTTP da associação ou Erro.
    """
    ticketId = int(instruction.chamadoId)
    itemId = int(instruction.itemId)
    itemTypeStr = instruction.tipoItem

    urlList = f"/Ticket/{ticketId}/Item_Ticket"
    try:
        resp = apiClient.get(urlList)
        if resp.status_code == 200:
            data = resp.json() or []
            for r in data:
                if int(r.get("items_id", 0)) == itemId and r.get("itemtype") == itemTypeStr:
                    return "Já associado anteriormente"
    except Exception as e:
        logger.warning(f"Não foi possível checar vínculos prévios: {e}")

    url = f"/Item_Ticket"
    payload = {
        "input": {
            "tickets_id": ticketId,
            "items_id": itemId,
            "itemtype": itemTypeStr,
        }
    }

    try:
        resp = apiClient.post(url, json=payload)
        resp.raise_for_status()
        return f"Assoc:{resp.status_code}"
    except Exception as e:
        logger.error(f"Erro ao associar item: {e}")
        return "Assoc:ERRO"


def removerItemDoChamado(apiClient, instruction: Instruction) -> str:
    """
    O que faz?
    Destrói a relação entre o Equipamento e o Chamado sem deletar o equipamento, disparando um método `DELETE` HTTP.

    Argumentos Necessários:
    - apiClient (ApiClient): Rede.
    - instruction (Instruction): Objeto contendo os IDs do Chamado e do Ativo.

    O que retorna? 
    - Mensagem informando a quantidade de vínculos removidos.
    """
    ticketId = instruction.chamadoId
    itemId = int(instruction.itemId)
    itemTypeStr = instruction.tipoItem

    urlList = f"/Ticket/{ticketId}/Item_Ticket"
    try:
        resp = apiClient.get(urlList)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Erro Listar vinculos: {e}")
        return f"List ERRO"

    data = resp.json() or []

    vinculos = [
        r
        for r in data
        if int(r.get("items_id", 0)) == itemId and r.get("itemtype") == itemTypeStr
    ]

    if not vinculos:
        return "Já estava removido"

    for v in vinculos:
        vincId = v.get("id")
        if not vincId:
            continue
        urlDel = f"/Item_Ticket/{vincId}"
        try:
            apiClient.delete(urlDel) 
        except Exception as e:
            logger.error(f"Erro ao remover vinculo: {e}")

    return f"Removidos {len(vinculos)} vínculos"


def executeFromParsedTask(apiClient, taskInstructions: List[Instruction]) -> tuple[List[Result], Optional[str]]:
    """
    O que faz?
    Orquestrador Operacional. Pega a lista de patrimônios mastigados, varre um por um, delega a transação de banco de dados e aciona a geração do Relatório de Auditoria.

    Argumentos Necessários:
    - apiClient (ApiClient): Rede.
    - taskInstructions (List[Instruction]): Fila de equipamentos a processar.

    O que retorna? 
    - Lista de objetos Result com o balanço patrimonial
    - Caminho físico do arquivo CSV gerado (ou None)
    """
    results: List[Result] = []

    sucessos = 0
    total = len(taskInstructions)
    logger.info(f"Iniciando execucao de {total} itens no GLPI...")

    for i, instruction in enumerate(taskInstructions, 1):
        result = processSingleAsset(apiClient, instruction)
        results.append(result)

        if result.success:
            sucessos += 1
        else:
            logger.warning(f"Falha na instrucao: {result.erro}")

    logger.info(f"{sucessos}/{total} itens concluidos com sucesso.")

    if results:
        csvFile = gerarHistoricoCsv(
            results,
            results[0].chamadoId,
            results[0].tarefaId,
        )
        return results, csvFile

    return results, None


def processSingleAsset(apiClient, instruction: Instruction) -> Result:
    """
    O que faz?
    O motor primário do projeto. Mapeia os status textuais do usuário para IDs de banco do GLPI, despacha comandos `PUT` para alterar os campos (Status, Local) e encapsula tudo na caixa Result.

    Argumentos Necessários:
    - apiClient (ApiClient): Rede.
    - instruction (Instruction): Objeto da instrução de apenas 1 equipamento.

    O que retorna? 
    - Objeto Result recheado com o status da ação
    """
    
    if not instruction.itemId:
        return Result(
            success=False,
            patrimonio=instruction.patrimonioItem, 
            itemId="N/A",
            chamadoId=instruction.chamadoId,
            tarefaId=instruction.tarefaId,
            tipoItem=instruction.tipoItem,
            lancStatusamento="STATUS_ANTES:N/A|STATUS_DEPOIS:N/A|LOCAL_ANTES:N/A|LOCAL_DEPOIS:N/A|UPDATE:N/A|ASSOC:N/A",
            action=instruction.acaoItem,
            erro="NOK - Item não cadastrado no GLPI"
        )
    
    patrimonio = instruction.patrimonioItem
    ticketId = instruction.chamadoId
    tarefaId = instruction.tarefaId
    itemId = int(instruction.itemId)
    itemType = instruction.tipoItem
    action = (instruction.acaoItem or "").lower()           
    textoStatus = (instruction.statusItem or "").lower()    
    novaLocal = instruction.localItem or ""                 

    statusAntes, localAntes = getStatusELocalItem(apiClient, itemType, str(itemId))

    if getattr(instruction, "already_done", False):
        lancStatus = (
            f"STATUS_ANTES:{statusAntes}"
            f"|STATUS_DEPOIS:{statusAntes}"
            f"|LOCAL_ANTES:{localAntes}"
            f"|LOCAL_DEPOIS:{localAntes}"
            f"|UPDATE:Sem alterações"
            f"|ASSOC:Já estava {'associado' if action == 'inserir' else 'removido'}"
        )
        return Result(
            success=True,
            patrimonio=patrimonio,
            itemId=str(itemId),
            chamadoId=ticketId,
            tarefaId=tarefaId,
            tipoItem=itemType,
            lancStatusamento=lancStatus,
            action=action,
            already_done=True,
        )

    mapStatus = {
        "ativo": 7,
        "desfeito": 13,
        "irrecuperável": 1,
        "obsoleto": 2,
        "ocioso": 12,
        "recuperavel": 11,
        "disponível para empréstimo": 8,
        "disponivel para emprestimo": 8,
        "em estoque": 5,
        "emprestado": 9,
        "manutenção": 3,
        "manutencao": 3,
    }
    realStatus = mapStatus.get(textoStatus)
    
    FonteAtualizacao = {
        "GLPI Native Inventory": 1,
        "FOG Server": 2,
        "ITXAutoNTI": 3
    }
    
    tagAtualizacao = FonteAtualizacao.get("ITXAutoNTI")

    fields: Dict[str, Any] = {}
    fields["id"] = itemId 
    fields['autoupdatesystems_id'] = tagAtualizacao

    if realStatus is not None:
        fields["states_id"] = realStatus

    if getattr(instruction, "localFuzzyCodigo", None):
        locId = getLocationIdByCode(apiClient, instruction.localFuzzyCodigo, instruction.localFuzzyNome)
        if locId:
            fields["locations_id"] = int(locId)

    msgUpdate = "Sem alterações"
    msgAssoc = "Sem associação"

    try:
        if len(fields) > 1: 
            itemUrl = f"/{itemType}/{itemId}"
            rUpdate = apiClient.put(itemUrl, json={"input": fields})
            msgUpdate = f"Upd:{rUpdate.status_code}"

        is_already_done = False
        if action == "inserir":
            msgAssoc = associarItemAoChamado(apiClient, instruction)
            if msgAssoc == "Já associado anteriormente":
                is_already_done = True
        elif action == "remover":
            msgAssoc = removerItemDoChamado(apiClient, instruction)
            if msgAssoc == "Já estava removido":
                is_already_done = True
        else:
            msgAssoc = f"Ação desconhecida: {instruction.acaoItem}"

        # Se não teve Update de status/local E a associação já estava feita, a tarefa estava totalmente pronta
        is_already_done = is_already_done and (msgUpdate == "Sem alterações")

        statusDepois, localApos = getStatusELocalItem(apiClient, itemType, str(itemId))

        if localApos and localApos != "?":
            localDepois = localApos
        else:
            localDepois = instruction.localFuzzyNome or localAntes

        lancStatus = (
            f"STATUS_ANTES:{statusAntes}"
            f"|STATUS_DEPOIS:{statusDepois}"
            f"|LOCAL_ANTES:{localAntes}"
            f"|LOCAL_DEPOIS:{localDepois}"
            f"|UPDATE:{msgUpdate}"
            f"|ASSOC:{msgAssoc}"
        )

        return Result(
            success=True,
            patrimonio=patrimonio,
            itemId=str(itemId),
            chamadoId=ticketId,
            tarefaId=tarefaId,
            tipoItem=itemType,
            lancStatusamento=lancStatus,
            action=action,
            already_done=is_already_done,
        )

    except Exception as e:
        lancStatus = (
            f"STATUS_ANTES:{statusAntes}"
            f"|STATUS_DEPOIS:ERRO"
            f"|LOCAL_ANTES:{localAntes}"
            f"|LOCAL_DEPOIS:{novaLocal or localAntes}"
            f"|UPDATE:ERRO"
            f"|ASSOC:ERRO"
        )
        return Result(
            success=False,
            patrimonio=patrimonio,
            itemId=str(itemId),
            chamadoId=ticketId,
            tarefaId=tarefaId,
            tipoItem=itemType,
            lancStatusamento=lancStatus,
            action=action,
            erro=str(e),
        )
