# Documentação: Automação de Chamados / Patrimônios via API do GLPI (Homolog)

**Ambiente API (homolog):** `https://servicoshomolog.ufabc.int.br/apirest.php/`


---

## Resumo objetivo

Esta documentação descreve pesquisa e automatização com a **API REST do GLPI** para:

- pesquisar todos os chamados **abertos no dia**;
- filtrar por **área** (grupo/department/custom field);
- obter detalhes de cada chamado, **extrair os patrimônios** indicados no formulário do chamado;
- **inserir/vincular** os patrimônios dentro do próprio chamado (ou campos relacionados).

O conteúdo incorpora conceitos discutidos na **reunião com o Mailsom** (uso dos métodos **GET / POST / PUT**, tratamento de erros, sessão, tokens) e traz exemplos práticos inspirados no script do Mailsom (anexado nesta documentação).

---

## 1. Contexto e referências

- **Endpoint homolog**: `https://servicoshomolog.ufabc.int.br/apirest.php/` (usar `https` e validar certificados se for o caso).  
- A API do GLPI trabalha via `apirest.php` e exige **App-Token** e autenticação de usuário (session token gerado por `initSession`).  
- Algumas chamadas de `search` usam parâmetros `criteria[...]` na URL e retornam blocos `data[]` com campos indexados (ex.: `.data[0]."2"` representa o campo 2 retornado). Teste no ambiente de homologação para confirmar quais índices correspondem a quais colunas.

---

## 2. Anotações sobre o script do Mailsom (fornecido)

Abaixo está o **script do Mailsom** (original), comentado com pontos importantes que podem ser reaproveitados:

```bash
#!/bin/bash
FOG_SERVER="http://fogserver.ufabc.int.br"
FOG_API_TOKEN=""
FOG_USER_TOKEN=""
SERIAL_NUMBER=$(dmidecode -s system-serial-number)

# Busca host no fog pelo serial e extrai hostname, user e inventário
response=$(curl -v -k -s   -H "fog-api-token: $FOG_API_TOKEN"   -H "fog-user-token: $FOG_USER_TOKEN"   -X GET "$FOG_SERVER/fog/host/search/$SERIAL_NUMBER")

HOSTNAME=$(echo "$response" | jq -r '.hosts[0].name')
# ... (mais extração de campos)

# Tokens de conexao do GLPI (ajustar para homolog)
USER_TOKEN=""
APP_TOKEN=""
GLPI_URL="https://servicos.ufabc.int.br/apirest.php"

# inicia sessao no GLPI
SESSION_TOKEN=$(curl -k -s -X GET     -H "Authorization: user_token $USER_TOKEN"     -H "App-Token: $APP_TOKEN"     "$GLPI_URL/initSession" | jq -r '.session_token')
```

**Pontos reaproveitáveis do script do Mailsom**:

- `initSession` + usar `Session-Token` em chamadas subsequentes; finalizar com `killSession`.  
- Uso do endpoint `/search/*` com `criteria` para localizar objetos (Computers, Users, Groups).  
- Como validar resultados: trata `null` e campos vazios antes de prosseguir.  
- Exemplo de `PUT` para atualizar objetos (`Computer/`), e `POST` para criar notas (`Notepad/`).

> **Atenção**: o script do Mailsom referencia `GLPI_URL="https://servicos.ufabc.edu.br/apirest.php"` (produção). Para homolog use `https://servicoshomolog.ufabc.int.br/apirest.php/` conforme informado.

---

## 3. Passo a passo operacional (com comandos exemplos)

### 3.1 Iniciar sessão (obter `Session-Token`)

São necessários dois tokens principais:

- **GLPI APP Token:** O3Sm8Qzq2K0jhdQdjTi1H9g76VM6LARTo2TcH1lP
- **User API Token:** mKTTxLYdMmIxav0PxnHCf6pNGATJAnyaNurXCCEI

```bash
curl -k -s -X GET   -H "Authorization: user_token YOUR_USER_TOKEN"   -H "App-Token: YOUR_APP_TOKEN"   "https://servicoshomolog.ufabc.int.br/apirest.php/initSession" | jq -r '.session_token'
```

**Observações**:
- Guarde `Session-Token` em variável de ambiente.  
- `-k` ignora validação de certificado; prefira remover em ambiente com certificado válido.  

### 3.2 Buscar chamados abertos no dia

A API de busca de tickets usa o endpoint `/search/Ticket` com parâmetros `criteria[...]`. Exemplo (montagem ilustrativa — ajuste `field`/`value` conforme sua instância):

```bash
# exemplo: filtrar por status aberto (field=4 ?), e data de criação hoje (field para date ~ consulte listSearchOptions)
curl -k -s -X GET  -H "App-Token: YOUR_APP_TOKEN"  -H "Session-Token: $SESSION_TOKEN"  "https://servicoshomolog.ufabc.int.br/apirest.php/search/Ticket?criteria[0][field]=4&criteria[0][searchtype]=equals&criteria[0][value]=1&criteria[1][field]=11&criteria[1][searchtype]=equals&criteria[1][value]=2025-10-16"
```

- **Importante**: os `field` números dependem da configuração da sua versão do GLPI; use `/listSearchOptions/Ticket` para descobrir quais campos existem e seus números.  

### 3.3 Filtrar por área

A "área" pode ser representada por campos diferentes (grupo, entidade, custom field). Ajuste `criteria` para o campo correto. Exemplo filtro por grupo (supondo que `field=12` represente o grupo):

```bash
...&criteria[2][field]=12&criteria[2][searchtype]=equals&criteria[2][value]=NOME_OU_ID_DA_AREA
```

### 3.4 Obter detalhes do Ticket

Para cada `ticket_id` obtido:

```bash
curl -k -s -X GET   -H "App-Token: YOUR_APP_TOKEN"   -H "Session-Token: $SESSION_TOKEN"   "https://servicoshomolog.ufabc.int.br/apirest.php/Ticket/{ticket_id}"
```

A resposta contém:
- campos padrão do ticket (title, content, status, dates)
- campos customizados (se configurados) — podem vir em `fields`, `input` ou em índices da `data[]` dependendo da versão/customização.

### 3.5 Extrair os patrimônios do formulário

Patrimônios podem estar:
- em campos customizados do ticket (campo texto com lista de números),
- em relações (itens vinculados ao ticket),
- em subformulários (se houver).

**Estratégia**:
1. Analise a estrutura da resposta do `Ticket/{id}` no homolog, identifique onde estão os valores (ex.: `fields`, `input`, `plugins` ou `data[...]`).
2. Se for campo texto com patrimonios separados por vírgula, parsear e normalizar (remover espaços, validar só números).
3. Para cada patrimônio, buscar se já existe no GLPI (`/search/Computer?criteria[...]` ou endpoint do item correspondente), ou criar se necessário.

Exemplo: buscar computador pelo patrimônio (`field` 2 costuma ser ID na listagem de `search/Computer`):

```bash
curl -k -s -X GET  -H "App-Token: YOUR_APP_TOKEN"  -H "Session-Token: $SESSION_TOKEN"  "https://servicoshomolog.ufabc.int.br/apirest.php/search/Computer?forcedisplay%5B0%5D%5B=2&criteria%5B0%5D%5Bfield%5D=2&criteria%5B0%5D%5Bsearchtype%5D=equals&criteria%5B0%5D%5Bvalue%5D=NUMERO_PATRIMONIO"
```

Note que `forcedisplay` serve para garantir quais colunas retornar; `".2"` frequentemente traz o ID.

### 3.6 Vincular (ou inserir) patrimônio no Ticket

Se desejar **vincular** um item existente ao ticket (associação), verifique a API para relacionamento de itens com tickets. Em muitos casos você atualiza o Ticket com itens no payload `items` ou cria registros em endpoints do tipo `Ticket_Item` / `Ticket_Itemtype` (varia por versão/plugin).

Exemplo genérico de `PUT` para atualizar um Ticket (adicionar campos/custom field):

```bash
curl -k -s -X PUT  -H "Content-Type: application/json"  -H "App-Token: YOUR_APP_TOKEN"  -H "Session-Token: $SESSION_TOKEN"  -d '{
   "input": {
     "id": TICKET_ID,
     "items": [
       { "items_id": PATRIMONIO_ID, "itemtype": "Computer" }
     ],
     "content": "Patrimônio(s) vinculados automaticamente: P12345"
   }
 }'  "https://servicoshomolog.ufabc.int.br/apirest.php/Ticket/TICKET_ID"
```

> Teste no homolog para confirmar se `items` é aceito. Algumas instalações esperam endpoints específicos ou payloads diferentes.  

---

## 4. Mapeamento de endpoints (relevantes)

- `initSession` — iniciar sessão. (GET)  
- `killSession` — encerrar sessão. (GET)  
- `search/Ticket` — pesquisar tickets com `criteria[...]`. (GET)  
- `Ticket/{id}` — detalhar ticket. (GET)  
- `Ticket/{id}` — atualizar ticket (PUT)  
- `Notepad/` — criar nota (POST)  
- `search/Computer` — procurar computadores/patrimônios. (GET)  
- `Computer/` — criar/atualizar computador (POST/PUT)  
- `Item_DeviceHardDrive/` — exemplo de subitem (POST/PUT)  

Use `/listSearchOptions/Ticket` (GET) para descobrir campos de pesquisa disponíveis na sua instância homolog.

---

## 5. Testes em ambiente de homologação (checklist prático)

1. Iniciar sessão e validar `Session-Token`.  
2. Executar `GET /listSearchOptions/Ticket` e documentar os `field` úteis (status, date_creation, group, customfields).  
3. Testar `search/Ticket` com critérios mínimos (status aberto) e verificar formato de retorno (`data[]` e índices).  
4. Para 1 ticket de teste: `GET /Ticket/{id}` e inspecionar onde o formulário armazena patrimônios.  
5. Testar criação/atualização leve: `PUT /Ticket/{id}` modificando `content` ou criando `Notepad` para validar permissões.  
6. Testar busca de patrimônio por número (usar `search/Computer` ou endpoint específico).  
7. Testar associação: tentar `PUT` com `items` e validar no GLPI se associação apareceu.  
8. Documentar respostas de erro comuns (401, 403, 404, 429, 500).

---

## 6. Limites de requisições, timeout e estratégias de robustez

- **Rate limiting**: não há um padrão único — verifique nos logs do GLPI/servidor ou com a equipe de infraestrutura. Em caso de respostas `429`, implemente *exponential backoff*.  
- **Timeout**: definir timeout nas requisições (ex.: 10s-30s).  
- **Retries**: para erros transitórios (5xx, 429) — tente 3 retries com backoff (ex.: 1s, 2s, 4s).  
- **Batch / paginação**: se houver muitos tickets, pagine as buscas (`glpilist_limit` ou equivalente) e processe por lotes.  
- **Logging**: registre ticket_id, tempo da requisição, payload e resposta.  
- **Monitoramento**: alerte em caso de falhas repetidas (ex.: > 10 erros em 1 hora).

---

## 7. Exemplo completo ()

> **Atenção**: este script é um *ponto de partida* — adapte nomes de campos, `field` e payload conforme o seu GLPI homolog.

```bash
#!/bin/bash
GLPI_URL="https://servicoshomolog.ufabc.int.br/apirest.php"
USER_TOKEN="SEU_USER_TOKEN"
APP_TOKEN="SEU_APP_TOKEN"
HOJE=$(date +%F) # YYYY-MM-DD

# inicia sessao
SESSION_TOKEN=$(curl -k -s -X GET   -H "Authorization: user_token $USER_TOKEN"   -H "App-Token: $APP_TOKEN"   "$GLPI_URL/initSession" | jq -r '.session_token')

if [ -z "$SESSION_TOKEN" ] || [ "$SESSION_TOKEN" == "null" ]; then
  echo "Falha ao obter session_token" >&2
  exit 1
fi

# buscar tickets abertos hoje (exemplo simplificado)
SEARCH_URL="$GLPI_URL/search/Ticket?criteria[0][field]=4&criteria[0][searchtype]=equals&criteria[0][value]=1&criteria[1][field]=11&criteria[1][searchtype]=equals&criteria[1][value]=$HOJE&glpilist_limit=100"
RESULTS=$(curl -k -s -X GET -H "App-Token: $APP_TOKEN" -H "Session-Token: $SESSION_TOKEN" "$SEARCH_URL")

# iterar sobre tickets encontrados
echo "$RESULTS" | jq -c '.data[]' | while read -r row; do
  TICKET_ID=$(echo "$row" | jq -r '."1"') # ajustar índice conforme retorno
  echo "Processando ticket $TICKET_ID"

  # obter detalhes
  TICKET_JSON=$(curl -k -s -X GET -H "App-Token: $APP_TOKEN" -H "Session-Token: $SESSION_TOKEN" "$GLPI_URL/Ticket/$TICKET_ID")

  # extrair campo onde estão os patrimônios (exemplo: campo custom 'xx' ou content)
  PATRIMONIOS_RAW=$(echo "$TICKET_JSON" | jq -r '.fields.customfield_patrimonios // .data[0]."XX" // .content')
  # normalize: separar por , ; espaço
  IFS=',; ' read -r -a PARRAY <<< "$PATRIMONIOS_RAW"

  for P in "${PARRAY[@]}"; do
    # limpar e validar se é número
    P=$(echo "$P" | tr -d ' ')

    if [[ "$P" =~ ^[0-9]+$ ]]; then
      # buscar patrimonio no GLPI
      RESP_PAT=$(curl -k -s -X GET -H "App-Token: $APP_TOKEN" -H "Session-Token: $SESSION_TOKEN" "$GLPI_URL/search/Computer?forcedisplay%5B0%5D%5B=2&criteria%5B0%5D%5Bfield%5D=2&criteria%5B0%5D%5Bsearchtype%5D=equals&criteria%5B0%5D%5Bvalue%5D=$P")

      PATR_ID=$(echo "$RESP_PAT" | jq -r '.data[0]."2"')
      if [ -n "$PATR_ID" ] && [ "$PATR_ID" != "null" ]; then
        # vincular (exemplo genérico, testar no homolog)
        PAYLOAD=$(jq -n --arg id "$TICKET_ID" --arg pid "$PATR_ID" '{input: {id: ($id|tonumber), items: [{items_id: ($pid|tonumber), itemtype: "Computer"}]}}')
        UPD=$(curl -k -s -X PUT -H "Content-Type: application/json" -H "App-Token: $APP_TOKEN" -H "Session-Token: $SESSION_TOKEN" -d "$PAYLOAD" "$GLPI_URL/Ticket/$TICKET_ID")
        echo "Vinculado patrimonio $P -> $PATR_ID no ticket $TICKET_ID"
      else
        echo "Patrimônio $P não encontrado no GLPI."
      fi
    fi
  done
done

# finalizar sessao
curl -k -s -X GET -H "App-Token: $APP_TOKEN" -H "Session-Token: $SESSION_TOKEN" "$GLPI_URL/killSession"
```

---

## 8. Possíveis melhorias e caminhos futuros

- Fazer versão em **Python** com `requests` para melhor tratamento de erros, logging e testes unitários.  
- Implementar cache local de patrimônios já verificados para reduzir buscas repetidas.  
- Criar **webhook**/gatilho se o GLPI suportar para rodar o processo na criação do ticket (ao invés de batch diário).  
- Dashboard com métricas de execução, falhas e número de vínculos efetuados.  

---

## 9. Conclusão

- Documente exatamente os `field` numéricos retornados por `search` e `listSearchOptions` no ambiente homolog da UFABC.  
- Teste todo fluxo em homolog antes de aplicar em produção.  
- O script do Mailsom é excelente base: ele já cobre autenticação, busca, mapeamento de modelos e atualização de itens — adapte a lógica de extração de patrimônios do ticket para o seu caso.  

---

## Anexo: script completo do Mailsom (colado pela equipe)
(cole aqui o script inteiro caso queira manter uma cópia na documentação)
