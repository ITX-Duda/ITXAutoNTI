<div align="center">

# 🚀 ITXAutoNTI

![status](https://img.shields.io/badge/status-%F0%9F%9A%A8%20Em%20Desenvolvimento-brightgreen?style=for-the-badge)
![license](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge&logo=mit)
![python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)


</div>

---

## 🧠 Arquitetura do Sistema

<table align="center" border="0">
  <tr>
    <td align="center">
      <img src="https://img.icons8.com/neon/96/code-fork.png" width="48px" alt="Módulo 1"><br>
      <strong>1. Retriever</strong><br>
      Busca tarefas "A fazer"
    </td>
    <td align="center"> ➡️ </td>
    <td align="center">
      <img src="https://img.icons8.com/neon/96/brain.png" width="48px" alt="Módulo 2"><br>
      <strong>2. Parser</strong><br>
      Interpreta a lógica
    </td>
    <td align="center"> ➡️ </td>
    <td align="center">
      <img src="https://img.icons8.com/neon/96/api.png" width="48px" alt="Módulo 3"><br>
      <strong>3. Executor</strong><br>
      Ação via API
    </td>
    <td align="center"> ➡️ </td>
    <td align="center">
      <img src="https://img.icons8.com/neon/96/checked.png" width="48px" alt="Módulo 4"><br>
      <strong>4. Closer</strong><br>
      Finaliza e Loga
    </td>
  </tr>
</table>

---

## ✨ Funcionalidades

Para replicar a "vibe" dos cartões flutuantes:

* 📚 **Leitura Inteligente:** O robô lê a tarefa exatamente como o analista escreveu.
* 📦 **Execução em Lote:** Associa múltiplos patrimônios ao chamado de uma só vez.
* ⚡ **Comunicação via API:** Realiza todas as operações diretamente na API do GLPI.
* 🦡 **O Texugo:** Responde automaticamente ao chamado informando o sucesso.
* 📊 **Histórico CSV:** Anexa o arquivo `ITX_Relatorio.csv` com logs detalhados.

---

## 🚀 Como Executar (Instalação e Uso)

Siga os passos abaixo para rodar o projeto localmente:

### Pré-requisitos
* Git e Python instalados.
* Acesso à API do GLPI configurado.

### Instalação

1.  **Clone este repositório:**
    ```bash
    git clone [https://github.com/ITX-Duda/ITXAutoNTI.git](https://github.com/ITX-Duda/ITXAutoNTI.git)
    ```

2.  **Acesse a pasta:**
    ```bash
    cd ITXAutoNTI
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inicie a engine:**
    ```bash
    python main.py
    ```

---
## 👨‍💻 A Equipe por trás da Automação

Este projeto não seria o mesmo sem o esforço conjunto dessa equipe. Um salve para os construtores do **ITXAutoNTI**:

<table align="center" border="0">
  <tr>
    <td align="center" valign="top">
      <a href="https://github.com/ITX-Duda">
        <img src="https://github.com/ITX-Duda.png" width="90px" style="border-radius: 50%;" alt="ITX-Duda"/><br>
        <sub><b>ITX-Duda</b></sub><br>
        <sub><i>Parser & Orchestrator</i></sub>
      </a>
    </td>
    <td align="center" valign="top">
      <a href="https://github.com/Zerik">
        <img src="https://github.com/Zerik.png" width="90px" style="border-radius: 50%;" alt="Zerik"/><br>
        <sub><b>Zerik</b></sub><br>
        <sub><i>Task Retriever</i></sub>
      </a>
    </td>
    <td align="center" valign="top">
      <a href="https://github.com/PedrolaLima">
        <img src="https://github.com/PedrolaLima.png" width="90px" style="border-radius: 50%;" alt="PedrolaLima"/><br>
        <sub><b>PedrolaLima</b></sub><br>
        <sub><i>Action Executor</i></sub>
      </a>
    </td>
    <td align="center" valign="top">
      <a href="https://github.com/Brnbb">
        <img src="https://github.com/Brnbb.png" width="90px" style="border-radius: 50%;" alt="Brnbb"/><br>
        <sub><b>Brnbb</b></sub><br>
        <sub><i>Task Closer</i></sub>
      </a>
    </td>
  </tr>
</table>

---
<p align="center">
  Feito por Equipe ITXAutoNTI!
</p
