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
from src.logic.task_executor import execute_from_parsed_task
from src.logic.task_closer import close_task

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
#Tasks 
    print("\n\n\n" + "-" * 60)
    print("👾⋆˚===== Task Retriever + Task Parser + Task Action =====˖°👾")
    print("-" * 60)
    print("Pesquisa dos chamados e das tasks que citam o ITXAutoNTI.\n")

    tasks = getItxTasks(sessionToken, appToken, apiUrl)

    for task in tasks:
        ticketId = str(task.get("ticketId") or "")
        taskId = str(task.get("taskId") or "")

        taskinstructions = parseTaskInstruction(task, sessionToken, appToken, apiUrl)

        for i, instr in enumerate(taskinstructions, 1):
            print(f"  {i}. {instr}")

        if taskinstructions:
            # CORREÇÃO AQUI: Desempacotar a tupla (resultados, arquivo_csv)
            resultados, csv_file = execute_from_parsed_task(sessionToken, appToken, apiUrl, taskinstructions)

            sucessos = 0
            total = len(resultados)
            for r in resultados:
                if isinstance(r, dict) and r.get("success") is True:
                    sucessos += 1
                elif hasattr(r, "success") and r.success:
                    sucessos += 1

            print(f"✅ {sucessos}/{total} executados com sucesso")

            # Closer AGORA PASSANDO A LISTA DE RESULTADOS
            close_resp = close_task(
                api_url=apiUrl,
                app_token=appToken,
                session_token=sessionToken,
                task_id=taskId,
                ticket_id=ticketId,
                resultados=resultados,  # <--- Passando a lista em vez de só os números
                csv_file=csv_file
            )

            print("📎 Closer:", close_resp.get("success"))
    print("\n" + "-" * 60)
    print("👾⋆˚===== Task Retriever + Task Parser - CONCLUÍDO =====˖°👾")
    print("-" * 60)

if __name__ == "__main__":
    exit(main())