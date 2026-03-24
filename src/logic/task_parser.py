import requests
import html
import re
import os 

from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict, Any
from collections import defaultdict

from src.logic.fuzzy_localizacao import getLocalizacaoFuzzy


@dataclass
class Instruction:
    itemId: str                 # index do equipamento
    patrimonioItem: str         # Prefixo+Numero
    statusItem: str             # Ativo/Desfazimento/Em andamento/Em manutenção
    acaoItem: str               # Inserir/Excluir
    localItem: str              # SS15/Depósito/Biblioteca
    localFuzzyNome: str
    localFuzzyCodigo: str
    tipoItem: str
    chamadoId: str
    tarefaId: str

    def __str__(self) -> str:
        return (
            f"Instruction("
            f"chamadoId={self.chamadoId}, "
            f"tarefaId={self.tarefaId}, "
            f"tipoItem={self.tipoItem}, "
            f"itemId={self.itemId}, "
            f"patrimonioItem={self.patrimonioItem}, "
            f"acaoItem={self.acaoItem}, "
            f"localItem={self.localItem}, "
            f"statusItem={self.statusItem}"
            f")"
        )


tipoMap = {
    "computador": "Computer",
    "computadores": "Computer",
    "computer": "Computer",
    "monitor": "Monitor",
    "monitores": "Monitor",
    "impressora": "Printer",
    "impressoras": "Printer",
    "dispositivos": "peripheral",  
    "dispositivo": "peripheral",
}

def normalizarNumero(n):
    return str(int(n))

def extrairCamposTask(textoHtml: str) -> dict:
    if not textoHtml:
        return {}

    # Limpeza inicial
    textoHtml = html.unescape(textoHtml)
    soup = BeautifulSoup(textoHtml, "html.parser")

    # Remove tabelas e a linha de dica para não interferir na contagem de (X)
    for tabela in soup.find_all("table"):
        tabela.decompose()
    
    texto = soup.get_text("\n", strip=True)
    
    # Remove a linha de dica especificamente para não contar o "(X)" de exemplo
    linhas = [l for l in texto.split("\n") if "* dica:" not in l.lower()]
    textoLimpo = "\n".join(linhas)

    # Regex que aceita qualquer caractere (ou espaço) dentro dos parênteses
    regexMarcador = r'\(\s*[^)\s]+\s*\)'

    # --- EXTRAÇÃO DA AÇÃO ---
    matchAcao = re.search(
        r'ação\s*:\s*(.+?)(?=status do ativo:|localiza[çc][aã]o do ativo:|$)',
        textoLimpo, re.IGNORECASE | re.DOTALL
    )

    valorAcao = None
    if matchAcao:
        blocoAcao = matchAcao.group(1)
        # Encontra todos os parênteses que NÃO estão vazios
        marcacoes = re.findall(regexMarcador, blocoAcao)
        
        if len(marcacoes) > 1:
            raise ValueError(f"Múltiplas ações marcadas {marcacoes}")
        
        if re.search(rf'{regexMarcador}\s*inserir', blocoAcao, re.IGNORECASE):
            valorAcao = "inserir"
        elif re.search(rf'{regexMarcador}\s*remover', blocoAcao, re.IGNORECASE):
            valorAcao = "remover"

    if not valorAcao:
        raise ValueError("Nenhuma ação marcada! Use (X) Inserir ou (X) Remover")

    # --- EXTRAÇÃO DO STATUS ---
    matchStatus = re.search(
        r'status do ativo\s*:\s*(.+?)(?=localiza[çc][aã]o do ativo:|$)',
        textoLimpo, re.IGNORECASE | re.DOTALL
    )
    
    valorStatus = None
    if matchStatus:
        blocoStatus = matchStatus.group(1).replace('\n', ' ') # Remove quebras de linha para a regex não falhar
        opcoesStatus = [
            "em estoque", "ativo", "desfeito", "irrecuperável", 
            "obsoleto", "disponível para empréstimo", "emprestado", 
            "manutenção", "ocioso"
        ]
        
        for opcao in opcoesStatus:
            if re.search(rf'{regexMarcador}\s*{re.escape(opcao)}', blocoStatus, re.IGNORECASE):
                valorStatus = opcao
                break

    # --- EXTRAÇÃO DA LOCALIZAÇÃO ---
    matchLocal = re.search(
        r'localiza[çc][aã]o do ativo\s*:\s*(.+)', 
        textoLimpo, re.IGNORECASE
    )
    local = matchLocal.group(1).strip() if matchLocal else None

    return {
        "acao": valorAcao,
        "statusAtivo": valorStatus, 
        "localizacao": local,       
    }

def extrairPatrimoniosPorTipo(textoHtml: str) -> dict:
    """Extrai números de patrimônio da tabela por tipo"""
    if not textoHtml:
        return {}

    textoHtml = html.unescape(textoHtml)
    soup = BeautifulSoup(textoHtml, "html.parser")

    resultado = defaultdict(list)

    for row in soup.find_all("tr")[1:]:  # pula cabeçalho
        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        tipo = cols[0].get_text(strip=True).lower()
        celula = cols[1].get_text(" ", strip=True)

        numeros = re.findall(r'\d+', celula)

        for n in numeros:
            resultado[tipo].append(normalizarNumero(n))

    # remove duplicados e ordena
    for tipo in resultado:
        resultado[tipo] = sorted(set(resultado[tipo]), key=int)

    return dict(resultado)

def findItemId(sessionToken: str, appToken: str, apiUrl: str, itemType: str, patrimonioItem: str) -> tuple[str, str] | None:
    
    if not itemType or itemType == "None":
        print(f"⚠️ Pulando busca: itemType inválido '{itemType}' para patrimônio {patrimonioItem}")
        return None
    
    headers = {
        "Content-Type": "application/json",
        "Session-Token": sessionToken,
        "App-Token": appToken
    }

    # =========================
    # BUSCA DOS CHAMADOS
    # =========================
    urlPesquisa = f"{apiUrl.rstrip('/')}/search/{itemType}"

    parametros = {
        "criteria[0][field]": "1", # patrimonio
        "criteria[0][searchtype]": "contains",
        "criteria[0][value]": patrimonioItem, 
        "forcedisplay[0]": "2",
        "forcedisplay[1]": "1",
    }
    
    resp = requests.get(urlPesquisa, headers=headers, params=parametros, verify=False)
    resp.raise_for_status()
    data = resp.json()
    resultado = data.get("data", [])
    
    if not resultado:
        return None

    primeiraColuna = resultado[0]
    itemId = primeiraColuna.get("2")  # id interno
    itemNome = primeiraColuna.get("1")  # nome (ex: UF038380)

    if not itemId or not itemNome:
        return None

    return str(itemId), str(itemNome)


def parseTaskInstruction(dadosTarefa: Dict[str, Any], sessionToken: str, appToken: str, apiUrl: str) -> List[Instruction]:

    chamadoId = str(dadosTarefa.get("ticketId") or dadosTarefa.get("ticket_id") or "")
    tarefaId = str(dadosTarefa.get("taskId") or dadosTarefa.get("task_id") or "")

    # Pega content da task
    content = dadosTarefa.get("content")
    if not content:
        print(f"❌ Task {tarefaId}: sem content")
        return []
    
    try:
        # Extrai tudo da task
        campos = extrairCamposTask(content)
        patrimoniosPorTipo = extrairPatrimoniosPorTipo(content)
        
        acaoItem = campos.get("acao")
        statusAtivo = campos.get("statusAtivo")
        localItem = campos.get("localizacao")
        
        # Validações (Status e Local agora são opcionais e não quebram o código)
        if not acaoItem:
            raise ValueError("Nenhuma ação marcada!")
        if not patrimoniosPorTipo:
            raise ValueError("Nenhum patrimônio na tabela!")
        
        print(f"✅ Task {tarefaId}: Ação: {acaoItem} / Status: {statusAtivo} / Local: {localItem}")
        
    except ValueError as e:
        print(f"❌ Task {tarefaId} inválida: {e}")
        return []
    
    instructions: List[Instruction] = []
    
    for tipo, listaIds in patrimoniosPorTipo.items():
        tipoGlpi = tipoMap.get(tipo.lower())
        if not tipoGlpi:
            print(f"⚠️ Tipo '{tipo}' não mapeado")
            continue
        
        for equipamentoId in listaIds:
            equipamentoIdStr = str(equipamentoId)
            
            # Chama o fuzzy com proteção caso o localItem venha vazio (None)
            matchLocal = getLocalizacaoFuzzy(localItem) if localItem else None
            fuzzyNome = matchLocal["Nome"] if matchLocal else ""
            fuzzyCodigo = matchLocal["Codigo"] if matchLocal else ""
            
            itemData = findItemId(sessionToken, appToken, apiUrl, tipoGlpi, equipamentoIdStr)
            
            # --- SE NÃO ACHOU NO GLPI, MANDA PRO CSV COM ERRO ---
            if not itemData:
                instructions.append(Instruction(
                    itemId="",  # Deixamos vazio para o executor saber que falhou
                    patrimonioItem=equipamentoIdStr, # Só o número digitado na task
                    chamadoId=chamadoId,
                    tarefaId=tarefaId,
                    acaoItem=acaoItem,
                    localItem=localItem or "",
                    localFuzzyNome=fuzzyNome,
                    localFuzzyCodigo=fuzzyCodigo,
                    statusItem=statusAtivo or "",
                    tipoItem=tipoGlpi,
                ))
                continue
            # ---------------------------------------------------
            
            # Se achou no GLPI, segue o jogo normal:
            itemId, itemNome = itemData
            
            instructions.append(Instruction(
                itemId=itemId,
                patrimonioItem=itemNome,
                chamadoId=chamadoId,
                tarefaId=tarefaId,
                acaoItem=acaoItem,
                localItem=localItem or "",
                localFuzzyNome=fuzzyNome,
                localFuzzyCodigo=fuzzyCodigo,
                statusItem=statusAtivo or "",
                tipoItem=tipoGlpi,
            ))
    
    return instructions