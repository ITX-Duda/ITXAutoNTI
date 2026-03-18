# src/logic/task_executor.py

import requests
import urllib3
import csv
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from src.logic.task_parser import Instruction

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def informacoesItem(apiUrl: str, headers: Dict[str, str], itemType: str, itemId: str) -> tuple[str, str]:
    
    url = f"{apiUrl.rstrip('/')}/{itemType}/{itemId}"
    
    params = {"expand_dropdowns": "true"}
    resp = requests.get(url, headers=headers, params=params, verify=False)

    if resp.status_code != 200:
        return f"ERRO_{resp.status_code}", "N/A"

    data = resp.json()

    statusName = str(data.get("states_id") or data.get("status") or "?")
    localName = str(data.get("locations_id") or data.get("location") or "?")
    
    return statusName, localName

@dataclass
class Result:
    success: bool
    patrimonio: str
    itemId: str
    chamadoId: str
    tarefaId: str
    tipoItem: str
    lancStatusamento: str  # string "ANTES:... | DEPOIS:... | Upd:... | Assoc:..."
    action: str
    erro: Optional[str] = None

    def __str__(self) -> str:
        return (
            f"Result(success={self.success}, patrimonio={self.patrimonio}, "
            f"status={self.lancStatusamento})"
        )

def localizacaoCod(apiUrl: str, headers: dict, codigo: str, nome: str) -> str:

    url = f"{apiUrl.rstrip('/')}/search/Location"
    
    tentativas = [codigo, nome]
    
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
                resp = requests.get(url, headers=headers, params=params, verify=False)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("data") and len(data["data"]) > 0:
                        id_interno = str(data["data"][0].get("2"))
                        if id_interno and id_interno != "None":
                            return id_interno
            except Exception:
                continue
                
    return None

def pegaStatusAtual(apiUrl: str, headers: Dict[str, str], itemType: str, itemId: int) -> str:
    url = f"{apiUrl.rstrip('/')}/{itemType}/{itemId}"
    resp = requests.get(url, headers=headers, verify=False)

    if resp.status_code != 200:
        return f"ERRO_GET_{resp.status_code}"

    data = resp.json()
    stateId = data.get("statusId") or "?"
    stateName = data.get("statusId_name") or "?"
    return f"{stateName} (ID:{stateId})"


def gerarHistoricoCsv(results: List[Result], chamadoId: str, tarefaId: str) -> str:
    # tá com erro, indo para a pasta errada
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    reports_dir = os.path.join(project_root, "relatorios")
    
    currentDir = os.getcwd()
    
    reports_dir = os.path.join(currentDir, "relatorios")
    os.makedirs(reports_dir, exist_ok=True)

    filename = f"historico_chamado_{chamadoId}_task_{tarefaId}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(reports_dir, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(
            [
                "Patrimônio",
                "Item ID",
                "Tipo",
                "Ação Solicitada",
                "Status Anterior",
                "Status Atual",
                "Localização Anterior",
                "Localização Depoios",
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

    print(f"📊 Histórico salvo: {filename}")
    return filepath


def inserirItem(apiUrl: str, headers: Dict[str, str],instruction: Instruction,) -> str:
    ticket_id = int(instruction.chamadoId)
    itemId = int(instruction.itemId)
    itemtype = instruction.tipoItem

    url = f"{apiUrl.rstrip('/')}/Item_Ticket"
    payload = {
        "input": {
            "tickets_id": ticket_id,
            "items_id": itemId,
            "itemtype": itemtype,
        }
    }

    resp = requests.post(url, headers=headers, json=payload, verify=False)

    return f"Assoc:{resp.status_code}"


def removerItem(apiUrl: str, headers: Dict[str, str], instruction: Instruction,) -> str:

    ticket_id = instruction.chamadoId
    itemId = int(instruction.itemId)
    itemtype = instruction.tipoItem

    url_list = f"{apiUrl.rstrip('/')}/Ticket/{ticket_id}/Item_Ticket"
    resp = requests.get(url_list, headers=headers, verify=False)
    if resp.status_code not in (200, 206):
        return f"List ERRO {resp.status_code}: {resp.text}"

    data = resp.json() or []

    vinculos = [
        r
        for r in data
        if int(r.get("items_id", 0)) == itemId and r.get("itemtype") == itemtype
    ]

    if not vinculos:
        return "Nenhum vínculo encontrado para remover"

    for v in vinculos:
        vinc_id = v.get("id")
        if not vinc_id:
            continue
        url_del = f"{apiUrl.rstrip('/')}/Item_Ticket/{vinc_id}"
        requests.delete(url_del, headers=headers, verify=False)

    return f"Removidos {len(vinculos)} vínculos"


def execucaoPosParser(sessionToken: str, appToken: str, apiUrl: str, taskInstructions: List[Instruction],) -> List[Result]:

    results: List[Result] = []

    headers = {
        "Content-Type": "application/json",
        "Session-Token": sessionToken,
        "App-Token": appToken,
    }

    sucessos = 0
    total = len(taskInstructions)
    print(f"🚀 Executando {total} instructions...")

    for i, instruction in enumerate(taskInstructions, 1):
        print(f"  {i:2d}/{total} {instruction.patrimonioItem} ({instruction.tipoItem})...")
        result = execucaoUnica(apiUrl, headers, instruction)
        results.append(result)

        if result.success:
            sucessos += 1
        else:
            print(f"    ❌ {result.erro}")

    print(f"✅ {sucessos}/{total} executados com sucesso")

    if results:
        csvFile = gerarHistoricoCsv(
            results,
            results[0].chamadoId,
            results[0].tarefaId,
        )
        print(f"📊 {csvFile}")
        return results, csvFile

    return results, None


def execucaoUnica(apiUrl: str, headers: Dict[str, str], instruction: Instruction,) -> Result:
    
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
    ticket_id = instruction.chamadoId
    tarefaId = instruction.tarefaId
    itemId = int(instruction.itemId)
    itemType = instruction.tipoItem
    action = (instruction.acaoItem or "").lower()
    textoStatus = (instruction.statusItem or "").lower()
    novaLocal = instruction.localItem or ""

    statusAntes, localAntes = informacoesItem(apiUrl, headers, itemType, itemId)

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

    fields: Dict[str, Any] = {}
    fields["id"] = int(itemId)

    if realStatus is not None:

        fields["statusId"] = realStatus


    if getattr(instruction, "localFuzzyCodigo", None):
        loc_id = localizacaoCod(apiUrl, headers, instruction.localFuzzyCodigo, instruction.localFuzzyNome)
        if loc_id:
            fields["locations_id"] = int(loc_id)
        else:
            print(f"⚠️ Aviso: ID numérico não encontrado no GLPI para o código {instruction.localFuzzyCodigo}")


    msgUpdate = "Sem alterações"
    msgAssoc = "Sem associação"

    try:
        if len(fields) > 1: 
            itemUrl = f"{apiUrl.rstrip('/')}/{itemType}/{itemId}"
            rUpdate = requests.put(
                itemUrl,
                headers=headers,
                json={"input": fields},
                verify=False,
            )
            msgUpdate = f"Upd:{rUpdate.status_code}"


        if action == "inserir":
            msgAssoc = inserirItem(apiUrl, headers, instruction)
        elif action == "remover":
            msgAssoc = removerItem(apiUrl, headers, instruction)
        else:
            msgAssoc = f"Ação desconhecida: {instruction.acaoItem}"

        statusDepois, _ = informacoesItem(apiUrl, headers, itemType, itemId)
        localDepois = novaLocal or localAntes

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
            chamadoId=ticket_id,
            tarefaId=tarefaId,
            tipoItem=itemType,
            lancStatusamento=lancStatus,
            action=action,
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
            chamadoId=ticket_id,
            tarefaId=tarefaId,
            tipoItem=itemType,
            lancStatusamento=lancStatus,
            action=action,
            erro=str(e),
        )
