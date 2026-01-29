from typing import List
from src.logic.task_parser import Instruction


def imprimirInstruction(instructions: List[Instruction]):
    print("\n📋 Resumo organizado das instruções:\n")

    for instruction in instructions:
        print(f"➡️  Ticket {instruction.parentTicketId} / Task {instruction.taskId}")
        print(f"    itemId     : {instruction.itemId}")
        print(f"    itemType   : {instruction.itemType}")
        print(f"    itemLoc    : {instruction.itemLoc}")
        print(f"    itemStatus : {instruction.itemStatus}")
        print(f"    actionType : {instruction.actionType}")
        print(f"    erro       : {instruction.errorMessage or 'OK'}\n")
