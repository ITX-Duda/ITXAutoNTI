# Automação GLPI – Estudo de Viabilidade com Bibliotecas Python

## Visão Geral
Este projeto visa automatizar a integração de grandes volumes de dados no **GLPI (Gestão Livre de Projetos de Informática)**.  
O objetivo é transformar dados tabulares (CSV/Excel) em **payloads JSON aninhados** e enviá-los com alta performance para a **REST API do GLPI**.

---

## Requisitos e Bibliotecas Selecionadas

| **Requisito**                | **Biblioteca** | **Justificativa Técnica**                                                                 |
|------------------------------|---------------|-------------------------------------------------------------------------------------------|
| **Requisições HTTP**        | `httpx`       | Suporte assíncrono, oferecendo ganhos de desempenho de até **7x** sobre `requests` em operações I/O-bound, compensando a ausência de endpoint bulk na API do GLPI. |
| **Leitura/Transformação**   | `pandas`      | Manipulação eficiente de grandes DataFrames e flexibilidade para gerar **JSON aninhado** via métodos vetorizados (`.apply`, `to_json(orient='records')`). |

---

## Detalhes Técnicos

### Gerenciamento de Sessão
- O cliente HTTP deve **persistir Session-Token e App-Token** em todas as chamadas.
- O objeto `httpx.AsyncClient` é essencial para manter o estado da sessão e configurar cabeçalhos padrão automaticamente.

### Simulação de Batch Upload
- O GLPI **não possui endpoint nativo para envio em massa**.
- A automação deve simular o batch enviando **requisições POST individuais de forma concorrente**.
- Implementação:
  - **Paralelismo com `asyncio.gather()`** para disparar corrotinas simultaneamente.
  - Minimiza tempo de espera de I/O e garante **alto throughput**.

---

## Fluxo da Automação
1. **Leitura dos dados** (CSV/Excel → DataFrame com `pandas`).
2. **Transformação** para JSON aninhado.
3. **Envio assíncrono** para API GLPI usando `httpx.AsyncClient`.

---

## Exemplo de Código
```python
import pandas as pd
import httpx
import asyncio

# Exemplo: leitura de CSV e transformação para JSON
df = pd.read_csv("dados.csv")
payloads = df.to_dict(orient="records")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def enviar(payload):
    async with httpx.AsyncClient(base_url="https://seu-glpi/api", headers={
        "App-Token": "SEU_APP_TOKEN",
        "Session-Token": "SEU_SESSION_TOKEN"
    }) as client:
        resp = await client.post("/endpoint", json=payload)
        resp.raise_for_status()
        return resp.json()

async def main():
    tasks = [enviar(p) for p in payloads]
    resultados = await asyncio.gather(*tasks, return_exceptions=True)
    print(resultados)

asyncio.run(main())
