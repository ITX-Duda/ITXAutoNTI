import sys
import os


currentDir = os.path.dirname(__file__)
projectRoot = os.path.abspath(os.path.join(currentDir, ".."))
sys.path.insert(0, projectRoot)

from src.utils.config_loader import chaves
from src.auth.session import autenticarGlpi
from src.data.reader import userName
from src.logic.task_parser import parseTaskInstruction, Instruction
from src.data.task_retriever import getItxTasks
from src.logic.task_reporter import imprimirInstruction
from src.data.aux import find_itx_mentions_in_tasks


def main():
    print("\n\n" + "-" * 60)
    print("🚀 ====== ITXConexão =====")
    print("-" * 60)

    print("\n🔍 1. Carregando configurações...")
    apiUrl = chaves.get("GLPI_API_URL")
    appToken = chaves.get("GLPI_APP_TOKEN")
    userToken = chaves.get("GLPI_USER_TOKEN")

    if not all([apiUrl, appToken, userToken]):
        print("❌ Erro: Configurações da API não encontradas no .env. Abortando.")
        return 

    print(f"✅ Configurações OK.")
#------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Autenticação
    print("\n🔐 2. Autenticando no GLPI...")
    sessionToken = autenticarGlpi(apiUrl, appToken, userToken)

    if sessionToken:
        userNome = userName(apiUrl, appToken, userToken, sessionToken)
    else:
        print("❌ Erro: Autenticação falhou! Verifique tokens no .env")
        return 1
    print("\n" + "-" * 60)
    print("🎉 === ITXConexão - CONCLUIDO ===")
    print("-" * 60)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Task Retriever 
    print("\n\n\n" + "-" * 60)
    print("👾⋆˚===== Task Retriever =====˖°👾")
    print("-" * 60)
    print("Apenas uma pesquisa dos chamados e das tasks que citam o ITXAutoNTI.\n")

    tasks = getItxTasks(sessionToken, appToken, apiUrl)

    print("\n" + "-" * 60)
    print("👾⋆˚===== Task Retriever - CONCLUÍDO =====˖°👾")
    print("-" * 60)

"""#------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Task Parser
    print("4. Task_Parser...")
    allInstructions: list[Instruction] = []
    for task in tasks:
        taskInstructions = parseTaskInstruction(task)
        allInstructions.extend(taskInstructions)

    imprimirInstruction(allInstructions)
"""
if __name__ == "__main__":
    exit(main())