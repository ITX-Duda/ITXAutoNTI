from dataclasses import dataclass
from typing import List


@dataclass
class Instruction:
    actionType: str          # inserir / atualizar / remover
    itemId: str              # ex: "MT000000", "UF000000"
    itemType: str            # ex: "Computador", "Monitor"
    itemLoc: str             # Localização
    itemStatus: str          # Status descritivo
    taskId: str              # ID da tarefa (TaskRetriever)
    parentTicketId: str      # ID do chamado principal (TaskRetriever)
    errorMessage: str = ""


def parseTaskInstruction(task_obj) -> List[Instruction]:

    instructions: List[Instruction] = []

    rawMessage = task_obj.rawMessage
    taskId = task_obj.taskId
    parentTicketId = task_obj.parentTicketId
    
    if not rawMessage:
        instructions.append(
            Instruction(
                actionType="",
                itemId="",
                itemType="",
                itemLoc="",
                itemStatus="",
                taskId=taskId,
                parentTicketId=parentTicketId,
                errorMessage="Mensagem vazia"
            )
        )
        return instructions

    lines = [l.strip() for l in rawMessage.splitlines() if l.strip()]

    currentType = ""
    currentStatus = ""
    currentLoc = ""

    for line in lines:
        if ":" in line and "status" in line.lower() and "local" in line.lower():
            header = line.split(":", 1)[0]

            parts = [p.strip() for p in header.split(",")]

            currentType = parts[0]

            for part in parts[1:]:
                lower = part.lower()
                if "status" in lower:
                    # depois de "status"
                    currentStatus = part.split(" ", 1)[1].strip()
                elif "local" in lower:
                    currentLoc = part.split(" ", 1)[1].strip()

            continue

        itemIds = line.split()
        for itemId in itemIds:
            instructions.append(
                Instruction(
                    actionType="insert",           
                    itemId=itemId,
                    itemType=currentType,
                    itemLoc=currentLoc,
                    itemStatus=currentStatus,
                    taskId=taskId,
                    parentTicketId=parentTicketId,
                    errorMessage=""
                )
            )

    if not instructions:
        instructions.append(
            Instruction(
                actionType="",
                itemId="",
                itemType="",
                itemLoc="",
                itemStatus="",
                taskId=taskId,
                parentTicketId=parentTicketId,
                errorMessage="Nenhum item encontrado na mensagem"
            )
        )

    return instructions
