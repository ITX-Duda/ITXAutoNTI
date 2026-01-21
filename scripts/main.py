import sys
import os


currentDir = os.path.dirname(__file__)
projectRoot = os.path.abspath(os.path.join(currentDir, ".."))
sys.path.insert(0, projectRoot)

from src.utils.config_loader import chaves
from src.auth.session import autenticarGlpi
from src.data.reader import userName
from src.logic.task_parser import parseTaskInstruction, Instruction
from src.data.task_retriever import getDailyTasksMock
from src.logic.task_reporter import imprimirInstruction


def main():
    print("🚀 === GLPI ITXAutoNTI CONECÇÃO ===\n")

    print("🔍 1. Carregando configurações...")
    apiUrl = chaves.get("GLPI_API_URL")
    appToken = chaves.get("GLPI_APP_TOKEN")
    userToken = chaves.get("GLPI_USER_TOKEN")

    if not all([apiUrl, appToken, userToken]):
        print("❌ Erro: Configurações da API não encontradas no .env. Abortando.")
        return 

    print(f"✅ Configurações OK: {apiUrl[:50]}...")

    print("\n🔐 2. Autenticando no GLPI...")
    sessionToken = autenticarGlpi(apiUrl, appToken, userToken)

    if sessionToken:
        userName(apiUrl, appToken, userToken, sessionToken)
    else:
        print("❌ Erro: Autenticação falhou! Verifique tokens no .env")
        return 1
    print("\n🎉 === CONEXÃO ITX CONCLUÍDA! ===")
    
    print("3. Task_Retriever (Mock)...")
    tasks = getDailyTasksMock()

    print("4. Task_Parser...")
    allInstructions: list[Instruction] = []
    for task in tasks:
        taskInstructions = parseTaskInstruction(task)
        allInstructions.extend(taskInstructions)

    imprimirInstruction(allInstructions)

if __name__ == "__main__":
    exit(main())