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
from src.logic.task_executor import executeFromParsedTask
from src.logic.task_closer import closeTask

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
# Autenticação
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
# Tasks 
    print("\n\n\n" + "-" * 60)
    print("👾⋆˚===== Task Retriever + Task Parser + Task Action =====˖°👾")
    print("-" * 60)
    print("Pesquisa dos chamados e das tasks que citam o ITXAutoNTI.\n")

    tasks = getItxTasks(sessionToken, appToken, apiUrl)

    for task in tasks:
        ticketId = str(task.get("ticketId") or "")
        taskId = str(task.get("taskId") or "")

        taskInstructions = parseTaskInstruction(task, sessionToken, appToken, apiUrl)

        for i, instr in enumerate(taskInstructions, 1):
            print(f"  {i}. {instr}")

        if taskInstructions:
            # Desempacotar a tupla (resultados, csvFile)
            resultados, csvFile = executeFromParsedTask(sessionToken, appToken, apiUrl, taskInstructions)

            sucessos = 0
            total = len(resultados)
            for r in resultados:
                if isinstance(r, dict) and r.get("success") is True:
                    sucessos += 1
                elif hasattr(r, "success") and r.success:
                    sucessos += 1

            print(f"✅ {sucessos}/{total} executados com sucesso")

            # Closer passando a lista de resultados e usando os parâmetros em camelCase
            closeResp = closeTask(
                apiUrl=apiUrl,
                appToken=appToken,
                sessionToken=sessionToken,
                taskId=taskId,
                ticketId=ticketId,
                resultados=resultados,
                csvFile=csvFile
            )

            print("📎 Closer:", closeResp.get("success"))
            
    print("\n" + "-" * 60)
    print("👾⋆˚===== Task Retriever + Task Parser - CONCLUÍDO =====˖°👾")
    print("-" * 60)

if __name__ == "__main__":
    exit(main())