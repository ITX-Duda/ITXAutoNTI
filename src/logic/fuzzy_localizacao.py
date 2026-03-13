import pandas as pd
import os
from fuzzywuzzy import fuzz, process

def getLocalizacaoFuzzy(LocalizacaoInput):
    if not LocalizacaoInput: 
        return None
        
    currentDir = os.path.dirname(os.path.abspath(__file__))
    csvPath = os.path.join(currentDir, "localizacao.csv")
    
    # O dropna() remove linhas/células vazias e resolve o erro do "float"
    tabelaLocalizacao = pd.read_csv(csvPath, sep=';', usecols=['Nome', 'Código'], dtype=str).dropna()
    df = pd.DataFrame(tabelaLocalizacao)

    # === SUA LÓGICA ORIGINAL ===
    matchFuzzy = process.extract(str(LocalizacaoInput), df["Nome"].tolist(), limit=10)
    matches = [m[0] for m in matchFuzzy]
    matchSub = process.extractOne(str(LocalizacaoInput), matches, scorer=fuzz.partial_ratio)
    # ===========================

    if matchSub:
        nome_encontrado = matchSub[0]
        # Pega a linha da planilha correspondente ao nome que sua lógica achou
        linha = df[df['Nome'] == nome_encontrado].iloc[0]
        
        return {
            "Nome": str(linha['Nome']),
            "Codigo": str(linha['Código'])
        }
        
    return None