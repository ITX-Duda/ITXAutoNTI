from dataclasses import dataclass
from typing import List


@dataclass
class MockTaskObject:
    taskId: str
    parentTicketId: str
    rawMessage: str
    errorMessage: str = ""


def getDailyTasksMock() -> List[MockTaskObject]:
    return [
        MockTaskObject(
            taskId="4444",
            parentTicketId="333333",
            rawMessage="""Computadores, status ATIVOS, local BIBLIOTECA:
UF040950 UF038844 UF040985 UF040779 UF040879 UF40871
UF065763 UF065758

Monitores, status EM ESTOQUE, local DEPÓSITO-NTI:
MT024626

Mesa de som, status DESFAZIMENTO, local SBC:
AV104351 AV104352 AV104353"""
        )
    ]
