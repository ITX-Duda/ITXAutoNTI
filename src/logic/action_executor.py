import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

import httpx

from src.data.sender import GlpiSender

logger = logging.getLogger(__name__)


@dataclass
class Instruction:
    actionType: str
    itemName: str
    ticketID: int
    itemType: Optional[str] = None
    itemLoc: Optional[str] = None
    itemStatus: Optional[str] = None


class ActionExecutor:
    """Versão reduzida e explícita do executor.

    Mantém apenas o necessário:
      - buscar ativo por `name` (Prefix+patrimônio)
      - atualizar campos já em formato GLPI (IDs numéricos)
      - associar o ativo a um ticket
    """

    def __init__(self, client: httpx.Client):
        self.client = client
        self.sender = GlpiSender(client)

    # Result helpers
    def _error_result(self, message: str, action: str, extra: Optional[Dict[str, Any]] = None):
        return {"success": False, "action_type": action, "message": message, "details": extra or {}}

    def _success_result(self, instruction: Instruction, item_id: int, status_message: str, details: Dict[str, Any]):
        return {
            "success": True,
            "action_type": instruction.actionType.lower(),
            "ticket_id": instruction.ticketID,
            "item_id": item_id,
            "id_identificado": instruction.itemName,
            "statusLancamento": status_message,
            "details": details,
        }

    def find_asset_id(self, name: str, item_type: str) -> Optional[int]:
        endpoint = f"/search/{item_type}"
        payload = {"criteria": [{"field": 1, "searchtype": "contains", "value": name}]}
        r = self.client.post(endpoint, json=payload)

        print(f"DEBUG API: Status {r.status_code} em {endpoint}")
        print(f"DEBUG Resposta: {r.text}") # Isso vai mostrar se a API reclamou do POST

        if r.status_code != 200:
            return None
        resp = r.json()
        if not resp or "data" not in resp or not resp["data"]:
            return None
        first = resp["data"][0]
        for k in ("id", "2", "1"):
            if k in first and first[k] not in (None, ""):
                try:
                    return int(first[k])
                except Exception:
                    return None
        for v in first.values():
            try:
                return int(v)
            except Exception:
                continue
        return None

    def get_item(self, item_type: str, item_id: int) -> Optional[dict]:
        r = self.client.get(f"/{item_type}/{item_id}")
        if r.status_code != 200:
            return None
        try:
            return r.json()
        except Exception:
            return None

    def update_item_fields(self, item_type: str, item_id: int, fields: Dict[str, Any]) -> Optional[dict]:
        if not fields:
            return None
        payload = {"input": {"id": item_id}}
        payload["input"].update(fields)
        r = self.client.put(f"/{item_type}/{item_id}", json=payload)
        if r.status_code != 200:
            return None
        try:
            return r.json()
        except Exception:
            return None

    def associate_item_to_ticket(self, ticket_id: int, item_id: int, item_type: str) -> Optional[dict]:
        payload = {"input": {"items_id": item_id, "itemtype": item_type}}
        r = self.client.post(f"/Ticket/{ticket_id}/Item", json=payload)
        if r.status_code != 200 and r.status_code != 201:
            return None
        try:
            return r.json()
        except Exception:
            return None

    def _build_asset_name(self, item_name_or_patrimony: str, item_type: Optional[str]) -> str:
        # comportamento simples: se for só dígitos, prefixamos conforme tipo conhecido
        prefixes = {"Computer": "UF", "Monitor": "MT", "Peripheral": "AV"}
        if item_name_or_patrimony.isdigit() and item_type:
            p = prefixes.get(item_type)
            if p:
                return f"{p}{item_name_or_patrimony}"
        return item_name_or_patrimony

    def executeInstruction(self, instruction: Instruction) -> Dict[str, Any]:
        action = instruction.actionType.lower().strip()
        
        # 1. Validação de Ticket (Necessário para quase todas as ações no contexto do GLPI)
        if not instruction.ticketID:
            return self._error_result("ticketID é obrigatório", action)

        # 2. Resolução do Ativo (A "Leitura" mencionada na imagem)
        name = self._build_asset_name(instruction.itemName, instruction.itemType)
        item_id = self.find_asset_id(name, instruction.itemType)
        
        if not item_id:
            return self._error_result(f"Ativo '{name}' não encontrado", action, {"searched_name": name})

        # 3. Direcionamento por Ação (Preparado para o futuro)
        try:
            if action == "inserir":
                return self._handle_insert(instruction, item_id)
            elif action == "atualizar":
                return self._handle_update(instruction, item_id)
            elif action == "remover":
                # placeholder para o futuro
                return self._error_result("Ação 'remover' ainda não implementada", action)
            else:
                return self._error_result(f"Ação '{action}' desconhecida", action)
        except Exception as e:
            logger.exception(f"Erro ao processar {action}: {e}")
            return self._error_result(str(e), action, {"item_id": item_id})

    def _handle_insert(self, instruction: Instruction, item_id: int) -> Dict[str, Any]:
        """Lógica específica para a ação de Inserir: apenas associar o ativo ao chamado."""
        current = self.get_item(instruction.itemType, item_id)

        # Associa ao ticket (A 'Inserção' propriamente dita no contexto do chamado)
        assoc = self.associate_item_to_ticket(instruction.ticketID, item_id, instruction.itemType)

        details = {
            "item_original": current,
            "alteracoes": {},
            "api_response": {"association": assoc}
        }
        return self._success_result(instruction, item_id, "Ativo vinculado ao chamado com sucesso", details)

    def _handle_update(self, instruction: Instruction, item_id: int) -> Dict[str, Any]:
        """Lógica específica para a ação de Atualizar: atualizar apenas os campos do ativo."""
        current = self.get_item(instruction.itemType, item_id)

        # Preparar campos a serem atualizados
        fields = {}
        if instruction.itemLoc: fields["locations_id"] = instruction.itemLoc
        if instruction.itemStatus: fields["states_id"] = instruction.itemStatus

        if not fields:
            return self._error_result("Nenhum campo para atualizar", instruction.actionType.lower())

        update_resp = self.update_item_fields(instruction.itemType, item_id, fields)

        details = {
            "item_original": current,
            "alteracoes": fields,
            "api_response": {"update": update_resp}
        }
        return self._success_result(instruction, item_id, "Ativo atualizado com sucesso", details)