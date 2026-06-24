<div align="center">

# 🤖 ITXAutoNTI
**Automação Inteligente de Tarefas no GLPI**

<p align="center">
  <img src="https://img.shields.io/badge/Release-v1.1.0-success?style=for-the-badge&logo=rocket" alt="Release" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge&logo=mit" alt="Licença" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
</p>

<p align="center">
  <a href="./README.md"><img src="https://img.shields.io/badge/🇺🇸_English-grey?style=flat-square" alt="English"/></a>
  <a href="./README.fr.md"><img src="https://img.shields.io/badge/🇫🇷_Français-grey?style=flat-square" alt="Français"/></a>
</p>

> *Transformando horas de trabalho manual em milissegundos de eficiência com RPA e integrações via API.*

</div>

---

## 📖 Visão Geral

O **ITXAutoNTI** é um robô de automação desenhado para interagir nativamente com o GLPI. Ele lê instruções, interpreta lógicas complexas e executa ações automatizadas na plataforma — como a associação em lote de múltiplos patrimônios a um chamado ou encerramento inteligente de tarefas.

Desenvolvido originalmente no **NTI (Núcleo de Tecnologia da Informação) da UFABC**, a ferramenta foi projetada para ser replicável por qualquer IFES ou organização que utilize o GLPI.

---

## 🧠 Arquitetura do Sistema

<div align="center">

| <img src="https://img.icons8.com/neon/96/code-fork.png" width="48px" alt="Módulo 1"><br>1. Retriever | ➡️ | <img src="https://img.icons8.com/neon/96/brain.png" width="48px" alt="Módulo 2"><br>2. Parser | ➡️ | <img src="https://img.icons8.com/neon/96/api.png" width="48px" alt="Módulo 3"><br>3. Executor | ➡️ | <img src="https://img.icons8.com/neon/96/checked.png" width="48px" alt="Módulo 4"><br>4. Closer |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Busca** tarefas ativas | | **Interpreta** a lógica | | **Executa** via API | | **Finaliza** e loga |

</div>

---

## ✨ Funcionalidades Principais

* 📚 **Leitura Inteligente:** O robô lê e entende a tarefa exatamente como o analista a escreveu.
* 📦 **Execução em Lote:** Associa múltiplos patrimônios ao chamado de forma simultânea.
* ⚡ **Comunicação Direta via API:** Executa todas as operações pela API REST do GLPI (rápido e invisível).
* 🦡 **Resposta Automática:** Responde ao chamado confirmando o sucesso da operação.
* 📊 **Histórico e Auditoria:** Anexa automaticamente o `ITX_Relatorio.csv` com logs detalhados.
* 🎯 **Fuzzy Matching de Localização:** Corrige automaticamente nomes de locais digitados com erro.

---

## 🚀 Como Executar

### 📋 Pré-requisitos
* **Python 3.8+**, **Git** e credenciais de acesso à **API do GLPI**.

### ⚙️ Instalação

```bash
git clone https://github.com/ITX-Duda/ITXAutoNTI.git
cd ITXAutoNTI
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Configure o arquivo `config/.env`:
```env
GLPI_API_URL="https://caminho-do-seu-glpi/apirest.php"
GLPI_APP_TOKEN="seu_app_token_gerado_no_glpi"
GLPI_USER_TOKEN="seu_user_token_gerado_no_glpi"
```

> **⚠️ Fuzzy Matching (Arquivo Privado):** O motor de localização requer o arquivo `localizacao.csv` em `src/logic/`. Este arquivo é sigiloso e não integra o repositório público — deve ser gerado pela instituição que fizer o deploy.

```bash
python main.py
```

---

## 📄 Publicação Científica

> **Automação e Otimização de Processos de TI na UFABC: O Desenvolvimento e Implementação do ITXAutoNTI**
> M. E. A. B. Brito, E. F. Lima, B. B. Bianchi, P. H. de Lima Franca, F. D. C. Iglesias
> *WTIFICES, CSBC 2026*

📎 [Artigo completo (PDF)](./Artigo_WTIFICES_ITXAutoNTI.pdf)

---

## 👨‍💻 Autores e Inventores

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

© 2026 Equipe ITXAutoNTI. O código-fonte, arquitetura e lógica do **ITXAutoNTI** constituem patrimônio intelectual desenvolvido pela equipe supracitada (`v1.1.0`). Todos os direitos reservados.

---

## 🙏 Créditos e Referências

| Projeto | Uso no ITXAutoNTI |
|---|---|
| [giovanny07/python-glpi-utils](https://github.com/giovanny07/python-glpi-utils) | Referência arquitetural para paginação dinâmica da API (limite de 50 itens) |
| [rapidfuzz/RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) | Motor de fuzzy matching para correção de localizações |
| [encode/httpx](https://github.com/encode/httpx) | Cliente HTTP moderno para comunicação estável com a API |

---

<p align="center">
  <img src="https://img.icons8.com/neon/96/bot.png" width="32px" alt="bot"><br>
  <b>Desenvolvido pela Equipe ITXAutoNTI!</b><br>
</p>
