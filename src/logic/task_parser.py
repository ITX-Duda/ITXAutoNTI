from dataclasses import dataclass
from typing import List, Dict
import re

@dataclass
class Instruction:
    ticket_id: str
    task_id: str
    action_type: str
    item_id: str  # PATRI000000
    item_loc: str  
    item_status: str  
    item_type: str  

def clean_glpi_content(raw_content: str) -> str:
    """Limpa HTML escapado do GLPI + padrões do seu print/log"""
    if not raw_content:
        return ""
    
    # Remove HTML
    clean = raw_content.replace("60br62", "\n")
    clean = raw_content.replace("60p62", "")
    clean = raw_content.replace("60span62", "")
    clean = re.sub(r"<[^>]+>", "", clean)
    clean = re.sub(r"&lt;|&gt;", "<>", clean)  # HTML entities
    clean = re.sub(r"\n+", "\n", clean)
    return clean.strip()

def parseTaskInstruction(task_data: Dict) -> List[Instruction]:
    raw_content = task_data.get("content", "")
    ticket_id = task_data.get("ticketid", "")
    task_id = task_data.get("taskid", "")
    
    clean_text = clean_glpi_content(raw_content)
    
    action = re.search(r"ao\s*:\s*(.*)", clean_text, re.IGNORECASE)
    loc = re.search(r"local\s*:\s*(.*)", clean_text, re.IGNORECASE)
    status = re.search(r"status\s*:\s*(.*)", clean_text, re.IGNORECASE)
    equips = re.search(r"equipamentos\s*:\s*(.*)", clean_text, re.IGNORECASE)
    
    base_action = action.group(1).strip() if action else "NA"
    base_loc = loc.group(1).strip() if loc else "NA"
    base_status = status.group(1).strip() if status else "NA"
    
    instructions: List[Instruction] = []
    
    if equips:
        lista_ids = [id_.strip() for id_ in equips.group(1).split(",") if id_.strip()]
        for id_pat in lista_ids:
            instructions.append(Instruction(
                ticket_id=ticket_id,
                task_id=task_id,
                action_type=base_action,
                item_id=f"PATRI{id_pat}",
                item_loc=base_loc,
                item_status=base_status,
                item_type="Computer"
            ))
    
    return instructions
