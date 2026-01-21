## 🟢 **Fase 1: Kickoff e Planejamento**

**Objetivo:** Alinhar a equipe, definir o escopo detalhado e estabelecer a base do projeto.

### **📝 Marco 1: Reunião de Alinhamento (Kickoff)**

- [x] **Criação do grupo de comunicação no Discord**(Responsável: Duda)
    
- [x] **Reunião de planejamento com o Sergio:** Apresentação do pré escopo inicial, alinhamento com ele sobre como documentar e como seguir o projeto sem perder tracking. (Responsável: Breno e Duda) 
	- **Nome do Projeto:** 
		- ITXAutoNTI
	- **Especifique a origem**: *(Os projetos podem ter origens variadas, por favor, especifique de quais origens surgiu a necessidade do projeto de acordo com a resposta anterior. Descreva, detalhadamente, o problema, necessidade ou oportunidade que originou a demanda.)* 
		- O projeto ITXAutoNTI surgiu da necessidade de automatizar tarefas manuais e repetitivas, que geram erros e inconsistências. A ideia é otimizar o tempo gasto com atividades padronizadas, liberando a equipe para focar em tarefas mais estratégicas e analíticas. O processo manual e repetitivo é o principal problema que o projeto busca resolver.
	- **Identificação de partes interessadas:** *(Relacionar quem/quais são os interessados no projeto, seja através de pessoas específicas, áreas ou instituições parceiras.)*
		- **Equipe do Projeto**: Breno, Pedro, Erik e Duda, que são os responsáveis por diversas etapas do projeto.
		- **Supervisores e Líderes**: Sergio, Mailsom e Felipe Dias, estão como supervisores e a Maria Eduarda como gestora, ambos ajudam no planejamento, alinhamento e definição da arquitetura do projeto.
		- **Especialistas Técnicos**: Dias e Mailsom, estão ajudando a alinhar a ideia, aprovar tecnicamente o projeto e validar o conhecimento sobre a API do GLPI.
		- **Usuários Finais**: A equipe do NTI, que utilizará a automação para inserir itens de patrimônio e, futuramente, para outras tarefas. Até o momento, nesse Alpha, seria  CGP e o Suporte.
	- **Escopo do projeto:** *(Delimitar qual é a expectativa de entrega do projeto como produto/serviço final.)*
		- O escopo do projeto é construir a primeira versão funcional de uma automação para a inserção de itens de patrimônio no sistema GLPI. Isso inclui as seguintes entregas:
			- **Fase 1: Kickoff e Planejamento**: Definição do escopo, pesquisa sobre a API do GLPI e bibliotecas Python, criação do repositório no GitHub, configuração do ambiente de desenvolvimento e documentação inicial.
			- **Fase 2: Desenvolvimento (Alpha)**: Implementação do código para autenticação na API, leitura de dados de entrada (por exemplo, arquivos CSV ou Excel), construção da requisição HTTP e envio para o endpoint da API. Esta fase também inclui a implementação de logs, tratamento de erros e testes de integração.
			- **Fase 3: Validação e Lançamento**: Refatoração e otimização do código, testes de cenários, criação de documentação para o usuário e preparação de uma apresentação de lançamento.
	- **Justificativas do projeto:** *(Por quê esse projeto é necessário?)*
		- O projeto ITXAutoNTI é necessário porque tarefas manuais e repetitivas, como a inserção de dados, levam a erros e inconsistências. A automação minimiza o erro humano, garantindo maior precisão. Além disso, o tempo gasto em cliques e repetições poderia ser melhor aproveitado em atividades mais estratégicas e analíticas
	- **Ganhos e/ou benefícios esperados:** *(Descrever os resultados a serem alcançados com o atendimento da demanda. O que se espera com a realização da demanda?)*
		- **Aumento de eficiência e precisão**: A automação minimiza os erros humanos, garantindo que os dados inseridos estejam sempre corretos.
		- **Liberação de tempo**: A equipe terá mais tempo para se dedicar a tarefas mais importantes e estratégicas, em vez de se focar em atividades manuais e repetitivas.
		- **Potencial de expansão**: O projeto, que começa com a inserção de patrimônios, pode ser expandido para automatizar outras tarefas, como o envio de mensagens e a atribuição de chamados.
	- **Data ideal para o início do projeto:** 
		- 10/2025 
	- **Data de conclusão esperada para o projeto:** 
		- 12/2025
			- *Baseando em um cenário otimista (Po) = 11/2025*
			- *Baseando em um cenário pessimista (Pp) = 01/2026*
			- *Baseando em um cenário mais provável (Pmp) = 12/2025* 
			
			**Prazo esperado = (Po + 4Pmp + Pp) / 6**
			= (11/2025 + 4×12/2025 + 01/2026) ÷ 6  
			= ==12/2025==
	
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
