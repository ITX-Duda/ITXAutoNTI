import html
import re
import os 

from bs4 import BeautifulSoup
from src.utils.logger import logger
from dataclasses import dataclass
from typing import List, Dict, Any
from collections import defaultdict

from src.logic.task_closer import getTaskAuthorMention, markTaskDone, createInfoTask
from src.logic.fuzzy_localizacao import getLocalizacaoFuzzy


@dataclass
class Instruction:
    """
    O que faz?
    Atua como uma 'Data Class' (Dicionário Estruturado de Dados). Armazena as informações mastigadas e traduzidas.
    """
    itemId: str                 
    patrimonioItem: str         
    statusItem: str             
    acaoItem: str               
    localItem: str              
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
    "telefone": "Phone",
    "telefones": "Phone",
    "dispositivos": "peripheral",  
    "dispositivo": "peripheral",
}

def normalizarNumero(n):
    """
    O que faz?
    Remove zeros à esquerda e garante que o número extraído do texto seja numérico válido.

    Argumentos Necessários:
    - n (str): O patrimônio lido na tabela.
    
    O que retorna? 
    - O número limpo em formato string.
    """
    return str(int(n))

def verificarSeJaProcessado(apiClient, itemType: str, itemId: str, acaoItem: str, chamadoId: str, localDesejadoCodigo: str, localDesejadoNome: str) -> bool:
    """
    O que faz?

    Valida se a ação (inserir/remover) já foi realizada para este chamado específico,
    evitando duplicidade de vínculos na tabela Item_Ticket e operações redundantes.
    """
    if not itemId or not chamadoId:
        return False

    try:
        # 1. Busca os vínculos atuais deste chamado para saber se o item já está associado a ele
        urlVinculos = f"/Ticket/{chamadoId}/Item_Ticket"
        respVinculos = apiClient.get(urlVinculos)
        respVinculos.raise_for_status()
        vinculos = respVinculos.json() or []

        # Varre a lista de vínculos do chamado
        jaEstaVinculado = any(
            int(v.get("items_id", 0)) == int(itemId) and v.get("itemtype") == itemType
            for v in vinculos
        )

        # 2. Busca o estado atual do ativo no GLPI
        urlItem = f"/{itemType}/{itemId}"
        respItem = apiClient.get(urlItem)
        respItem.raise_for_status()
        dadosAtuais = respItem.json()
        localAtualId = str(dadosAtuais.get("locations_id", ""))

        if acaoItem == "inserir":   
            from src.logic.task_executor import getLocationIdByCode
            # Converte o código string do Fuzzy para o ID de banco real do GLPI
            localDesejadoId = getLocationIdByCode(apiClient, localDesejadoCodigo, localDesejadoNome)
            
            # Se já está vinculado ao chamado E a localização já está correta, o trabalho está feito
            if jaEstaVinculado and localDesejadoId and localAtualId == str(localDesejadoId):
                return True
                
        elif acaoItem == "remover":
            # Se a ação é remover e o item NÃO está mais vinculado ao chamado, a operação já foi concluída
            if not jaEstaVinculado:
                return True

        return False

    except Exception as e:
        # Bloco unificado de exceção
        logger.error(f"Erro ao verificar estado de duplicidade/estado atual do item {itemId} no chamado {chamadoId}: {e}")
        # Por segurança, se a API falhar na checagem, retornamos False para permitir que o sistema tente processar a instrução
        return False

def extrairCamposTask(textoHtml: str) -> dict:
    """
    O que faz?
    Faz a Análise Léxica (Parsing Regex). Lê o texto rico HTML, joga fora a formatação visual e usa Expressões Regulares para encontrar quais opções (Checkboxes) o usuário preencheu.

    Argumentos Necessários:
    - textoHtml (str): O conteúdo HTML bruto capturado da tarefa.

    O que retorna? 
    - Dicionário com 'acao', 'statusAtivo' e 'localizacao'.
    """
    if not textoHtml:
        return {}

    textoHtml = html.unescape(textoHtml)
    soup = BeautifulSoup(textoHtml, "html.parser")

    for tabela in soup.find_all("table"):
        tabela.decompose()
    
    texto = soup.get_text("\n", strip=True)
    linhas = [l for l in texto.split("\n") if "* dica:" not in l.lower()]
    textoLimpo = "\n".join(linhas)

    regexMarcador = r'\(\s*[^)\s]+\s*\)'

    matchAcao = re.search(
        r'ação\s*:\s*(.+?)(?=status do ativo:|localiza[çc][aã]o do ativo:|$)',
        textoLimpo, re.IGNORECASE | re.DOTALL
    )

    valorAcao = None
    if matchAcao:
        blocoAcao = matchAcao.group(1)
        marcacoes = re.findall(regexMarcador, blocoAcao)
        
        if len(marcacoes) > 1:
            raise ValueError(f"Múltiplas ações marcadas {marcacoes}")
        
        if re.search(rf'{regexMarcador}\s*inserir', blocoAcao, re.IGNORECASE):
            valorAcao = "inserir"
        elif re.search(rf'{regexMarcador}\s*remover', blocoAcao, re.IGNORECASE):
            valorAcao = "remover"

    if not valorAcao:
        raise ValueError("Nenhuma ação marcada! Use (X) Inserir ou (X) Remover")

    matchStatus = re.search(
        r'status do ativo\s*:\s*(.+?)(?=localiza[çc][aã]o do ativo:|$)',
        textoLimpo, re.IGNORECASE | re.DOTALL
    )
    
    valorStatus = None
    if matchStatus:
        blocoStatus = matchStatus.group(1).replace('\n', ' ') 
        
        opcoesStatus = [
            "em estoque", "ativo", "desfeito", "irrecuperável", 
            "obsoleto", "disponível para empréstimo", "emprestado", 
            "manutenção", "ocioso"
        ]
        
        for opcao in opcoesStatus:
            if re.search(rf'{regexMarcador}\s*{re.escape(opcao)}', blocoStatus, re.IGNORECASE):
                valorStatus = opcao
                break

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
    """
    O que faz?
    Processador de Tabela Dinâmica. Varre a tabela HTML, capta a relação [Tipo Equipamento] -> [Números de Patrimônio] e empacota os dados de forma limpa.

    Argumentos Necessários:
    - textoHtml (str): O conteúdo bruto HTML da tarefa.

    O que retorna? 
    - Agrupamento em Dicionário relacionando os tipos e as listas de códigos de patrimônios.
    """
    if not textoHtml:
        return {}

    textoHtml = html.unescape(textoHtml)
    soup = BeautifulSoup(textoHtml, "html.parser")

    resultado = defaultdict(list)

    for row in soup.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        tipo = cols[0].get_text(strip=True).lower()
        celula = cols[1].get_text(" ", strip=True)

        numeros = re.findall(r'\d+', celula)

        for intervalo in re.finditer(r'(\d+)\s*(?:a|até|ate|-|–)\s*(\d+)', celula, re.IGNORECASE):
            patrimonioInicial = int(intervalo.group(1))
            patrimonioFinal = int(intervalo.group(2))
            if(patrimonioFinal > patrimonioInicial):
                for patrimonio in range(patrimonioInicial + 1, patrimonioFinal):
                    numeros.append(str(patrimonio))
        for n in numeros:
            resultado[tipo].append(normalizarNumero(n))

    for tipo in resultado:
        resultado[tipo] = sorted(set(resultado[tipo]), key=int)

    return dict(resultado)

def findItemId(apiClient, itemType: str, patrimonioItem: str) -> tuple[str, str] | None:
    """
    O que faz?
    Busca no banco GLPI o UUID numérico invisível do equipamento que a API exige para fazer qualquer Update.

    Argumentos Necessários:
    - apiClient (ApiClient): Cliente de rede.
    - itemType (str): Tipo traduzido do equipamento.
    - patrimonioItem (str): O número do patrimônio.

    O que retorna? 
    - ID Numérico Banco
    - Nome Completo do Patrimônio
    """
    
    if not itemType or itemType == "None":
        logger.warning(f"Pulando busca: itemType inválido '{itemType}' para patrimônio {patrimonioItem}")
        return None

    urlPesquisa = f"/search/{itemType}"

    parametros = {
        "criteria[0][field]": "1", 
        "criteria[0][searchtype]": "contains",
        "criteria[0][value]": patrimonioItem, 
        "forcedisplay[0]": "2", 
        "forcedisplay[1]": "1", 
    }
    
    try:
        resp = apiClient.get(urlPesquisa, params=parametros)
        resp.raise_for_status()
        data = resp.json()
        resultado = data.get("data", [])
    except Exception as e:
        logger.error(f"Erro ao buscar item {patrimonioItem}: {e}")
        return None
    
    if not resultado:
        return None

    primeiraColuna = resultado[0]
    itemId = primeiraColuna.get("2")    
    itemNome = primeiraColuna.get("1")  

    if not itemId or not itemNome:
        return None

    return str(itemId), str(itemNome)


def parseTaskInstruction(dadosTarefa: Dict[str, Any], apiClient) -> List[Instruction]:
    """
    O que faz?
    O Maestro deste Módulo. É o funil que engole os dados vindos do Retriever e aglutina todas as funções, devolvendo as Instruções Finais formatadas.

    Argumentos Necessários:
    - dadosTarefa (Dict): Os parâmetros brutos da tarefa.
    - apiClient (ApiClient): Cliente de rede.

    O que retorna? 
    - Fila de ações lineares limpas para a etapa de execução de transações.
    """

    chamadoId = str(dadosTarefa.get("ticketId") or dadosTarefa.get("ticket_id") or "")
    tarefaId = str(dadosTarefa.get("taskId") or dadosTarefa.get("task_id") or "")

    content = dadosTarefa.get("content")
    if not content:
        logger.error(f"ERRO! Task {tarefaId}: sem content")
        return []
    
    try:
        campos = extrairCamposTask(content)
        patrimoniosPorTipo = extrairPatrimoniosPorTipo(content)
        
        acaoItem = campos.get("acao")
        statusAtivo = campos.get("statusAtivo")
        localItem = campos.get("localizacao")
        
        if not acaoItem:
            raise ValueError("Nenhuma ação marcada!")
        if not patrimoniosPorTipo:
            raise ValueError(" Nenhum patrimônio na tabela!")
        
    except ValueError as e:
        logger.error(f"Task {tarefaId} inválida: {e}")
        
        mention = getTaskAuthorMention(apiClient, int(tarefaId))
        
        message = (
            f"{mention},<br><br>"
            f"❌ Ocê verificou direito? A tarefa está inválida.<br><br>" 
            f"Confira se a ação foi marcada corretamente ou se esqueceu de inserir os patrimônios na tabela."
            f"<br><br>"
            f"<small><i>*Mensagem gerada automaticamente via automação (ITXAutoNTI v1.2.0)</i></small><br><br>"
        )
        
        createInfoTask(apiClient, int(chamadoId), message)
        markTaskDone(apiClient, tarefaId) #Encerra tarefa inválida

        return []
    
    instructions: List[Instruction] = []
    
    for tipo, listaIds in patrimoniosPorTipo.items():
        tipoGlpi = tipoMap.get(tipo.lower())
        if not tipoGlpi:
            logger.warning(f"Tipo '{tipo}' não mapeado")
            continue
        
        for equipamentoId in listaIds:
            equipamentoIdStr = str(equipamentoId)
            
            matchLocal = getLocalizacaoFuzzy(localItem) if localItem else None
            fuzzyNome = matchLocal["Nome"] if matchLocal else ""
            fuzzyCodigo = matchLocal["Codigo"] if matchLocal else ""
            
            itemData = findItemId(apiClient, tipoGlpi, equipamentoIdStr) 
            
            if not itemData:
                instructions.append(Instruction(
                    itemId="",
                    patrimonioItem=equipamentoIdStr,
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
            
            itemId, itemNome = itemData
            
            # ==========================================
            # Validação de Item Duplicado
            jaFoiProcessado = verificarSeJaProcessado(
                            apiClient=apiClient,
                            itemType=tipoGlpi,
                            itemId=itemId,
                            acaoItem=acaoItem,
                            chamadoId=chamadoId,                # Enviando o ID do chamado atual
                            localDesejadoCodigo=fuzzyCodigo,    # Código vindo do Fuzzy
                            localDesejadoNome=fuzzyNome         # Nome vindo do Fuzzy
                        )

            if jaFoiProcessado:
                logger.info(
                    f"Ignorando patrimônio {itemNome} ({itemId}): "
                    f"A ação '{acaoItem}' já se encontra aplicada para o chamado #{chamadoId} no GLPI."
                    )
                continue # Pula o append da instrução e vai para o próximo equipamento

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