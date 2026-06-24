import os
import logging
from datetime import datetime

def setupLogger():
    """
    O que faz?
    Configura e inicializa o sistema de logs da aplicação.
    Assegura que todas as informações de execução, avisos e erros sejam salvos permanentemente em arquivos textuais no diretório /logs para auditoria.

    O que retorna?
    - Instância global e formatada do logger da aplicação
    """
    projectRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    logDir = os.path.join(projectRoot, "logs")
    
    os.makedirs(logDir, exist_ok=True)
    
    logFileName = f"ITXExecucao.log"
    logPath = os.path.join(logDir, logFileName)
    
    logger = logging.getLogger("ITXAutoNTI")
    logger.setLevel(logging.INFO) 
    
    if not logger.handlers:
        fileHandler = logging.FileHandler(logPath, mode='a', encoding='utf-8')
        fileHandler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        fileHandler.setFormatter(formatter)
        
        logger.addHandler(fileHandler)
        
    return logger

logger = setupLogger()
