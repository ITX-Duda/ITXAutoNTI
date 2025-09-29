## **🟢 Fase 1: Kickoff e Planejamento**

**Objetivo:** Alinhar a equipe, definir o escopo detalhado e estabelecer a base do projeto.

### **📝 Marco 1: Reunião de Alinhamento (Kickoff)**

- [x] **Criação do grupo de comunicação no Discord**(Responsável: Duda)
    
- [ ] Reunião de planejamento com o Sergio: Apresentação do pré escopo inicial, alinhamento com ele sobre como documentar e como seguir o projeto sem perder tracking. (Responsável: Breno e Duda) 
	
- [ ] **Reunião de Kickoff com a equipe (Breno, Pedro e Erik)**
    - [ ] **Discussão e Refinamento do Escopo:** Abrir o projeto para sugestões e considerações dos estagiários, alterações, opniões, o que concordam, algo a acrescentar, o que melhorar, onde querem contribuir, etc.

---

### **📝 Marco 2: Análise e Pesquisa**

- [ ] **Pesquisa sobre a API do GLPI:** Aprofundar na documentação da API, focando nos endpoints necessários para a criação de itens. 
    
- [ ] **Pesquisa de Bibliotecas Python:** Pesquisar as bibliotecas mais adequadas para lidar com requisições HTTP e a leitura de dados de entrada (como arquivos CSV ou Excel). 
    
- [ ] Alinhar com Dias e/ou Mailsom:** Alinhar a ideia, obter aprovação técnica e discutir a viabilidade de acesso aos ambientes de teste e homologação.  (talvez seja melhor depois de ter algo iniciado, tipo algum protótipo e quando for testar chamar eles)
	- [ ] **Dias:** Apresentar a ideia e discutir a viabilidade de desenvolvimento e validação do código.
	- [ ] **Mailsom:** Validar o conhecimento sobre a API do GLPI.

---

### **📝 Marco 3: Estrutura e Documentação Inicial**

- [x] **Criar o repositório no GitHub* (Responsável: Duda)
     [ITXAutoNTI](https://github.com/mbrito-d/ITXAutoNTI)
- [ ] **Configurar o ambiente de desenvolvimento:** Garantir que todos os membros da equipe tenham o Python e as ferramentas necessárias instaladas. (Responsáveis: Todos)
    
- [ ] **Desenhar a arquitetura do projeto:** Com a ajuda do Sergio, definir a estrutura de pastas e arquivos para o projeto. (Responsáveis: Duda e Breno)
    
- [ ] **Criar o `README.md` detalhado:** Documentar o propósito do projeto, as tecnologias usadas e as instruções para o setup inicial, já que ele trabalha diretamente com planejamento. 
    

---

## **🟡 Fase 2: Desenvolvimento da Automação (Alpha)**

**Objetivo:** Construir a primeira versão funcional (Alpha) da automação para a inserção de patrimônios.

### **📝 Marco 4: Implementação Principal**

- [ ] **Código de Autenticação na API:** A equipe pode trabalhar em conjunto para implementar a função que lida com a autenticação na API do GLPI.
    
- [ ] **Leitura de Dados de Entrada:** Definir o formato dos dados (CSV, por exemplo) e escrever a função para ler e processar esses dados. 
    
- [ ] **Construção da Requisição HTTP:** Criação e envio da requisição para o endpoint da API, já que eles conhecem bem o fluxo no GLPI. 
    

---

### **📝 Marco 5: Testes e Tratamento de Erros**

- [ ] **Implementação de Logs e Erros:** Adicionar tratamento de erros robusto para lidar com falhas de conexão, dados inválidos ou problemas na API. 
    
- [ ] **Testes de Integração:** Garantir que a automação adicione os itens corretamente no ambiente de homologação. (Responsáveis: Todos)
    
---

## **🟠 Fase 3: Validação e Lançamento**

**Objetivo:** Otimizar o código, criar a documentação final e preparar a apresentação para o lançamento.

### **📝 Marco 6: Otimização e Finalização**

- [ ] **Refatoração do Código:** Revisar e otimizar o código para performance e legibilidade, aplicando as melhores práticas. 
    
- [ ] **Teste de Cenários:** Garantir que a automação lide com diferentes casos, como arquivos de entrada vazios ou com dados incorretos.
    

---

### **📝 Marco 7: Apresentação e Documentação**

- [ ] **Documentação do Usuário:** Criar um guia simples, com instruções passo a passo para que qualquer pessoa possa usar a automação. 
    
- [ ] **Preparação da Apresentação:** Criar os slides e a demonstração final para a apresentação ao seu supervisor e à equipe. 
