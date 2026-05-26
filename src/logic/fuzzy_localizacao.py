import pandas as pd
import os
from rapidfuzz import fuzz, process

SCORE_CUTOFF = 85

def getLocalizacaoFuzzy(LocalizacaoInput):
    """
    O que faz?
    Atua como um motor de busca tolerante a falhas. Compara a localização digitada com o banco de locais oficiais do GLPI e encontra a correspondência mais próxima usando a lógica difusa.

    Argumentos Necessários:
    - LocalizacaoInput (str): O texto cru da localização fornecido pelo usuário na tarefa.

    O que retorna? 
    - Dicionário contendo o Nome e o Codigo do local
    - Retorna a localização matriz da instituição caso não alcance o grau de precisão mínimo
    """
    
    if not LocalizacaoInput: 
        return None
        
    currentDir = os.path.dirname(os.path.abspath(__file__))
    csvPath = os.path.join(currentDir, "localizacao.csv")
    
    tabelaLocalizacao = pd.read_csv(csvPath, sep=';', usecols=['Nome', 'Código'], dtype=str).dropna()
    df = pd.DataFrame(tabelaLocalizacao)

    matchFuzzy = process.extractOne(
        str(LocalizacaoInput), 
        df["Nome"].tolist(), 
        scorer=fuzz.token_set_ratio, 
        score_cutoff=SCORE_CUTOFF
    )

    if matchFuzzy:
        nomeEncontrado = matchFuzzy[0]
        linha = df[df['Nome'] == nomeEncontrado].iloc[0]
        
        return {
            "Nome": str(linha['Nome']),
            "Codigo": str(linha['Código'])
        }
        
    return {
        "Nome": "FUNDAÇÃO UNIVERSIDADE FEDERAL DO ABC",
        "Codigo": "UFABC" 
    }
