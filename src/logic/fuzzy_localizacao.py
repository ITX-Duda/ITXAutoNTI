import pandas as pd
import os
from fuzzywuzzy import fuzz, process

SCORE_CUTOFF = 85

def getLocalizacaoFuzzy(LocalizacaoInput):
    if not LocalizacaoInput: 
        return None
        
    currentDir = os.path.dirname(os.path.abspath(__file__))
    csvPath = os.path.join(currentDir, "localizacao.csv")
    
    # O dropna() remove linhas/células vazias e resolve o erro do "float"
    tabelaLocalizacao = pd.read_csv(csvPath, sep=';', usecols=['Nome', 'Código'], dtype=str).dropna()
    df = pd.DataFrame(tabelaLocalizacao)

    
    # === token_set_ratio: ignora a ordem das palavras e palavras duplicadas ===
    matchFuzzy = process.extractOne(str(LocalizacaoInput), df["Nome"].tolist(), scorer=fuzz.token_set_ratio, score_cutoff=SCORE_CUTOFF)
    # ==========================================================================

    if matchFuzzy:
        nome_encontrado = matchFuzzy[0]
        # Pega a linha da planilha correspondente ao nome que sua lógica achou
        linha = df[df['Nome'] == nome_encontrado].iloc[0]
        
        return {
            "Nome": str(linha['Nome']),
            "Codigo": str(linha['Código'])
        }
        
        # Caso não exista match com score igual ou acima do estabelecido, retorna a localização padrão UFABC
    return {
        "Nome": "FUNDAÇÃO UNIVERSIDADE FEDERAL DO ABC",
        "Codigo": "UFABC" 
    }
