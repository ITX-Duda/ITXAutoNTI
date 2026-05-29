<div align="center">

# 🤖 ITXAutoNTI
**Automação Inteligente de Tarefas no GLPI**

<p align="center">
  <img src="https://img.shields.io/badge/Release-v1.2.0-success?style=for-the-badge&logo=rocket" alt="Status" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge&logo=mit" alt="License" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
</p>

> *Transformando horas de trabalho manual em milissegundos de eficiência com RPA e integrações via API.*

</div>

---

## 📖 Visão Geral

O **ITXAutoNTI** é um robô de automação desenhado para interagir nativamente com o GLPI. Ele é capaz de ler instruções, interpretar lógicas complexas e executar ações automatizadas na plataforma, como a associação em lote de múltiplos patrimônios a um chamado ou encerramento inteligente de tarefas.

---

## 🧠 Arquitetura do Sistema

O fluxo de processamento é dividido em quatro módulos principais, operando em esteira:

<div align="center">

| <img src="https://img.icons8.com/neon/96/code-fork.png" width="48px" alt="Módulo 1"><br>1. Retriever | ➡️ | <img src="https://img.icons8.com/neon/96/brain.png" width="48px" alt="Módulo 2"><br>2. Parser | ➡️ | <img src="https://img.icons8.com/neon/96/api.png" width="48px" alt="Módulo 3"><br>3. Executor | ➡️ | <img src="https://img.icons8.com/neon/96/checked.png" width="48px" alt="Módulo 4"><br>4. Closer |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Busca** tarefas ativas | | **Interpreta** a lógica | | **Executa** via API | | **Finaliza** e loga |

</div>

---

## ✨ Funcionalidades Principais

* 📚 **Leitura Inteligente:** O robô lê e entende a tarefa exatamente como o analista a escreveu.
* 📦 **Execução em Lote:** Capacidade de associar múltiplos patrimônios ao chamado de forma simultânea.
* ⚡ **Comunicação Direta via API:** Executa todas as operações diretamente na API REST do GLPI (rápido e invisível).
* 🦡 **Resposta Automática:** Responde automaticamente ao chamado informando o sucesso da operação.
* 📊 **Histórico e Auditoria:** Anexa automaticamente o arquivo `ITX_Relatorio.csv` com logs detalhados e status das ações.
* 🎯 **Fuzzy Matching de Localização:** Algoritmo inteligente de IA que corrige e aproxima nomes de locais digitados com erro pelo usuário, baseando-se em um dicionário de dados local e privado da instituição.

---

## 🚀 Como Executar

Siga os passos abaixo para preparar o seu ambiente e rodar o projeto localmente:

### 📋 Pré-requisitos
* **Python 3.8+** instalado na máquina.
* **Git** para clonar o repositório.
* Credenciais de acesso à **API do GLPI**.

### ⚙️ Instalação

**1. Clone o repositório:**
```bash
git clone https://github.com/ITX-Duda/ITXAutoNTI.git
cd ITXAutoNTI
```

**2. Crie e ative um ambiente virtual (Recomendado):**
```bash
# No Windows
python -m venv venv
.\venv\Scripts\activate

# No Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**4. Configure as chaves de segurança e o ambiente:**
Crie ou edite o arquivo `.env` (ou dentro da pasta `config/`) e adicione **obrigatoriamente** as seguintes credenciais da API do GLPI:
```env
GLPI_API_URL="https://caminho-do-seu-glpi/apirest.php"
GLPI_APP_TOKEN="seu_app_token_gerado_no_glpi"
GLPI_USER_TOKEN="seu_user_token_gerado_no_glpi"
```
> **⚠️ Importante sobre o Fuzzy Matching (Arquivo Privado):** 
> O motor de correção inteligente de localizações precisa consultar um arquivo chamado `localizacao.csv` alocado na pasta `src/logic/`. Por conter o mapeamento interno da infraestrutura da instituição, **este arquivo é sigiloso e não faz parte do repositório público**. Quem for instalar ou realizar o deploy da aplicação deverá gerar e providenciar essa base em CSV contendo os locais internos para que a engine funcione corretamente.

**5. Inicie a engine:**
```bash
python main.py
```

---

## 👨‍💻 Autores e Inventores

Este projeto é fruto da pesquisa, dedicação e genialidade de uma equipe focada em otimização. Um grande *salve* para os criadores do **ITXAutoNTI**:

<table align="center" border="0">
  <tr>
    <td align="center" valign="top">
      <a href="https://github.com/ITX-Duda">
        <img src="https://github.com/ITX-Duda.png" width="90px" style="border-radius: 50%; border: 3px solid #3776AB;" alt="ITX-Duda"/><br>
        <sub><b>ITX-Duda</b></sub><br>
        <sub><i>Parser & Orchestrator</i></sub>
      </a>
    </td>
    <td align="center" valign="top">
      <a href="https://github.com/Zerik">
        <img src="https://github.com/Zerik.png" width="90px" style="border-radius: 50%; border: 3px solid #3776AB;" alt="Zerik"/><br>
        <sub><b>Zerik</b></sub><br>
        <sub><i>Task Retriever</i></sub>
      </a>
    </td>
    <td align="center" valign="top">
      <a href="https://github.com/PedrolaLima">
        <img src="https://github.com/PedrolaLima.png" width="90px" style="border-radius: 50%; border: 3px solid #3776AB;" alt="PedrolaLima"/><br>
        <sub><b>PedrolaLima</b></sub><br>
        <sub><i>Task Executor</i></sub>
      </a>
    </td>
    <td align="center" valign="top">
      <a href="https://github.com/Brnbb">
        <img src="https://github.com/Brnbb.png" width="90px" style="border-radius: 50%; border: 3px solid #3776AB;" alt="Brnbb"/><br>
        <sub><b>Brnbb</b></sub><br>
        <sub><i>Task Closer</i></sub>
      </a>
    </td>
  </tr>
</table>

---

## ⚖️ Propriedade Intelectual e Licenciamento

**Registro de Propriedade Intelectual:**
O código-fonte, arquitetura, design e lógica do sistema **ITXAutoNTI** constituem patrimônio intelectual desenvolvido pela equipe supracitada. Este repositório reflete a versão oficial `v1.0.0` para fins de registro formal e documentação de autoria.

**Aviso de Direitos:**
© 2026 Equipe ITXAutoNTI. 
Todos os direitos reservados. O uso, modificação ou distribuição de partes ou da totalidade deste software deve respeitar as condições estabelecidas no modelo de licenciamento aplicável a este repositório.

---

<p align="center">
  <img src="https://img.icons8.com/neon/96/bot.png" width="32px" alt="bot"><br>
  <b>Desenvolvido pela Equipe ITXAutoNTI!</b><br>
</p>
