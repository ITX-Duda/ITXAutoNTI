from typing import List
from src.logic.task_parser import Instruction

def imprimirInstruction(instructions: List[Instruction]):
    """
    Exibe as instruções de forma organizada e tabular no terminal,
    agrupadas por Chamado e Task (Lote).
    """
    if not instructions:
        print("\n⚠️ Nenhuma instrução encontrada para exibir.")
        return

    # Usaremos um conjunto para rastrear quais Tasks já imprimimos o cabeçalho
    current_task = None
    
    print("\n" + "=" * 85)
    print(f"{'📋 RELATÓRIO DE PROCESSAMENTO DE LOTES (ITXAutoNTI)':^85}")
    print("=" * 85)

    for inst in instructions:
        # Se mudou a Task, imprime o cabeçalho do novo lote
        if inst.task_id != current_task:
            print(f"\n🔹 LOTE: taskId = {inst.task_id} | ticketId = {inst.ticket_id}")
            print(f"{'-' * 85}")
            # Cabeçalho da Tabela
            print(f"{'Patrimônio':<18} | {'Tipo':<12} | {'Status':<10} | {'Ação':<10} | {'Local':<15}")
            print(f"{'-' * 85}")
            current_task = inst.task_id
        
        # Linha do Equipamento
        print(f"{inst.itemID:<18} | {inst.itemType:<12} | {inst.itemStatus:<10} | {inst.actionType:<10} | {inst.itemLoc:<15}")

    print("\n" + "=" * 85)
    print(f"{'FIM DO RELATÓRIO':^85}")
    print("=" * 85 + "\n")