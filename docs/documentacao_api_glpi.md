# Documentação da API do GLPI

---

## Introdução

Durante reunião com o Mailsom, ele compartilhou boas ideias de como estruturar integrações com APIs, especialmente nos métodos **PUT / GET / POST** e como pensar em falhas, limites e boas práticas de chamadas. Esta documentação combina essas ideias com pesquisa sobre a API do GLPI, para embasar o desenvolvimento de um script automatizado que:

- consulta os chamados abertos no dia,
- filtra por área,
- abre/obtém os detalhes do chamado,
- extrai os patrimônios listados no formulário do chamado,
- insere (ou atualiza) esses patrimônios *dentro* do chamado (associação ou campo apropriado).

---

## 1. Visão Geral da API do GLPI

- A API REST do GLPI está integrada ao endpoint `apirest.php` (por padrão).
- Ela permite operações CRUD (Create, Read, Update, Delete) nos principais objetos do GLPI.
- É possível operar Tickets, Itens/Patrimônios, Documentos, Usuários e outros.
- Algumas versões exigem parâmetros específicos e possuem limitações de permissão.

---

## 2. Autenticação e Sessão

### 2.1 Tokens

São necessários dois tokens principais:

- **GLPI APP Token:** O3Sm8Qzq2K0jhdQdjTi1H9g76VM6LARTo2TcH1lP  
- **User API Token:** mKTTxLYdMmIxav0PxnHCf6pNGATJAnyaNurXCCEI

### 2.2 Iniciar Sessão (`initSession`)

```bash
curl -X GET   -H "Content-Type: application/json"   -H "Authorization: user_token YOUR_USER_TOKEN"   -H "App-Token: YOUR_APP_TOKEN"   "https://seu_glpi_domain/apirest.php/initSession"
```

Resposta esperada:

```json
{
  "session_token": "abc123def456..."
}
```

### 2.3 Finalizar Sessão (`killSession`)

```bash
curl -X GET   -H "Session-Token: SEU_SESSION_TOKEN"   -H "App-Token: SEU_APP_TOKEN"   "https://seu_glpi_domain/apirest.php/killSession"
```

---

## 3. Endpoints Relevantes e Funcionamento

| Objeto / funcionalidade | Método HTTP | Endpoint / caminho            | Uso                           |
| ----------------------- | ----------- | ----------------------------- | ----------------------------- |
| Tickets (listar)        | GET         | `/search/Ticket`              | Buscar tickets abertos no dia |
| Ticket (detalhar)       | GET         | `/Ticket/{id}`                | Obter dados do chamado        |
| Ticket (atualizar)      | PUT         | `/Ticket/{id}`                | Inserir patrimônio            |
| Patrimônio              | POST/GET    | `/Computer`, `/Printer`, etc. | Criar ou buscar item          |
| Campos disponíveis      | GET         | `/listSearchOptions/Ticket`   | Entender filtros possíveis    |

---

## 4. Fluxo Sugerido do Script

1. Ler documentação oficial da API.  
2. Mapear endpoints necessários.  
3. Testar endpoints em ambiente de homologação.  
4. Identificar limites de requisições e tempos de resposta.  
5. Criar script que:  
   - Busca tickets abertos hoje.  
   - Filtra por área.  
   - Extrai patrimônios.  
   - Atualiza o ticket com os patrimônios correspondentes.  

---

## 5. Boas Práticas e Considerações

- Manter tokens seguros (não expor em código).  
- Fechar sessão após o uso.  
- Implementar logs e tratamento de erros.  
- Respeitar limites de requisição (rate limits).  
- Testar em ambiente de homologação antes da produção.  

---

## 6. Exemplo Estrutural (Pseudo‑Código Python)

```python
def iniciar_sessao(base_url, app_token, user_token):
    # Autenticação inicial
    ...

def buscar_tickets_abertos_do_dia(...):
    # Busca tickets abertos no dia
    ...

def atualizar_ticket_com_patrimonio(ticket_id, patrimonio_id):
    # Atualiza ticket inserindo patrimônio
    ...

def processo_principal():
    # Fluxo principal
    ...
```

---

## 7. Conclusão

Esta documentação foi criada com base na reunião com **Mailsom**, que explicou conceitos de requisições HTTP (**PUT, GET, POST**) e ajudou a direcionar a pesquisa sobre a API do GLPI.  
O resultado é um guia para estruturar um script automatizado, seguro e eficiente para manipulação de chamados e patrimônios no sistema.

---
