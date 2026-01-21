# 📖 Documentação da Arquitetura (ITXAutoNTI)

Este documento é um guia didático que explica a estrutura de pastas, os ficheiros-chave e os comandos que usamos para desenvolver este projeto.

## 1. O "Porquê": De Script para Projeto

A primeira pergunta a ser feita é: "Porquê tanta pasta, se o código cabia num ficheiro só?"

A resposta é que passamos de um **script** para um **projeto**.

* Um **script** é feito para ser executado e resolver um problema imediato.
* Um **projeto** é feito para ser mantido, atualizado e melhorado ao longo do tempo, por múltiplas pessoas.

Adotámos esta arquitetura por 4 motivos principais:

1.  **Segurança 🛡️:** **NUNCA** enviamos segredos (tokens, senhas, URLs) para o GitHub. Eles ficam isolados num ficheiro `.env` que é ignorado.
2.  **Manutenabilidade 🔧:** Quando a API do GLPI mudar, saberemos exatamente qual ficheiro corrigir (ex: `src/auth/session.py`) sem ter de ler 800 linhas de código.
3.  **Organização 📦:** Cada pasta tem uma única responsabilidade (Separação de Responsabilidades). `src/` guarda as "ferramentas", `scripts/` "usa" as ferramentas.
4.  **Trabalho em Equipe 🤝:** Esta estrutura permite que 4 pessoas trabalhem em partes diferentes (um no login, outro na leitura de dados) ao mesmo tempo, sem que um apague o trabalho do outro.

---

## 2. A Estrutura de Pastas (O Mapa do Projeto)

Esta é a "planta baixa" do nosso projeto.

```
ITXAutoNTI/
│
├── .git/              <-- (O "cérebro" do Git, fica oculto)
├── .github/           <-- (Ficheiros de automação do GitHub, ex: Issues)
├── .gitignore         <-- O "Porteiro" do Git
│
├── config/
│   ├── .env           <-- O "Cofre" com os segredos (IGNORADO PELO GIT)
│   └── .env.example   <-- O "Molde" do cofre (VAI PARA O GIT)
│
├── docs/              <-- (Manuais, diagramas, documentação)
│
├── scripts/
│   └── run_team_test.py <-- O ficheiro que NÓS EXECUTAMOS
│
├── src/
│   ├── __init__.py    <-- (Diz ao Python que 'src' é um módulo)
│   ├── auth/          <-- Gaveta da Autenticação
│   │   └── session.py
│   ├── data/          <-- Gaveta de Leitura/Escrita de Dados
│   │   └── reader.py
│   └── utils/         <-- Gaveta de "Ajudantes"
│       └── config_loader.py
│
├── tests/             <-- (A nossa "Rede de Segurança" para testes)
│
├── requirements.txt   <-- A "Lista de Compras" de bibliotecas
└── venv/              <-- A "Bolha" de bibliotecas (IGNORADA PELO GIT)
```

---

## 3. O Porquê de Cada Ficheiro e Pasta-Chave

### 📂 `src/` (Source/Fonte)
* **O que é?** É o "coração" do nosso projeto. Contém todo o nosso código Python que pode ser reutilizado. São as nossas "ferramentas".
* **Porquê?** Separamos o código principal (`src/`) dos scripts que o executam (`scripts/`).
* **`src/auth/`**: Gaveta só para coisas de login.
* **`src/data/`**: Gaveta só para ler e escrever dados no GLPI.
* **`src/utils/`**: Gaveta para "ajudantes" que outros módulos usam.

### 📂 `scripts/`
* **O que é?** Contém os ficheiros que nós **executamos** no terminal (ex: `python scripts/run_team_test.py`).
* **Porquê?** Estes scripts são os "trabalhadores". Eles vão até a `src/` (a "caixa de ferramentas"), pegam as ferramentas que precisam (como `autenticar_glpi`) e usam-nas para fazer um trabalho.

### 📂 `config/`
* **O que é?** O nosso "cofre".
* **`config/.env`**: O ficheiro **secreto**. Contém os tokens e senhas reais. **É IGNORADO PELO GIT**.
* **`config/.env.example`**: O "molde" ou "exemplo". É um ficheiro que **VAI PARA O GIT** e mostra aos outros programadores quais variáveis eles precisam de criar no `.env` deles.

### 📄 `src/utils/config_loader.py`
* **O que é?** É o "Chaveiro".
* **Porquê?** É o único script que sabe onde o "cofre" (`config/.env`) está. Ele abre o cofre e carrega os segredos para a memória do programa, para que o resto do código (como `session.py`) os possa usar em segurança, sem nunca saber quais são os tokens reais.

### 📄 `.gitignore`
* **O que é?** O "Porteiro" do Git.
* **Porquê?** É uma lista de ficheiros e pastas que o Git deve **IGNORAR**. Os mais importantes que estão lá:
    * `venv/` (Para não enviar 10.000 ficheiros de bibliotecas)
    * `config/.env` (Para não enviar os nossos segredos)
    * `__pycache__/` (Ficheiros temporários do Python)

### 📄 `requirements.txt`
* **O que é?** A "Lista de Compras" do projeto.
* **Porquê?** Lista todas as bibliotecas (`httpx`, `python-dotenv`) que o projeto precisa. Quando um colega novo entra, ele não precisa de adivinhar: apenas roda `pip install -r requirements.txt` e o seu `venv` é preenchido com tudo o que é necessário.

### 📂 `venv/`
* **O que é?** O nosso "Ambiente Virtual" ou "Bolha".
* **Porquê?** Quando instalamos uma biblioteca (ex: `httpx`), ela é instalada *dentro* desta bolha, e não no seu Windows. Isso impede que os projetos interfiram uns com os outros. **É IGNORADO PELO GIT.**

---

## 4. O Mistério do `sys.path` (O Erro `ModuleNotFoundError`)

**O Problema:** Quando executamos `python scripts/run_team_test.py`, o Python só sabe procurar por `imports` dentro da pasta `scripts/`. Ele não consegue "ver" a pasta `src/` que está "ao lado", noutro diretório.

**A Solução:** O código "mágico" que colocámos no topo do `run_team_test.py`:

```python
import sys
import os
# --- Mágica para o Python encontrar a pasta 'src' ---
# Pega o caminho do diretório atual (scripts)
current_dir = os.path.dirname(__file__)
# Sobe um nível para a pasta raiz (ITXAutoNTI)
project_root = os.path.abspath(os.path.join(current_dir, ".."))
# Adiciona a raiz ao 'caminho' do Python
sys.path.insert(0, project_root)
# ----------------------------------------------------

# Agora este import funciona!
from src.auth.session import autenticar_glpi
```

* **O que faz (em português):** "Descobre onde está a pasta principal (`ITXAutoNTI/`) e adiciona-a à lista de locais onde o Python deve procurar por módulos."
* Graças a isto, a linha `from src.auth.session import ...` funciona.

---

## 5. Guia de Comandos Essenciais (PowerShell)

Estes são os comandos que usamos no dia-a-dia.

### 1. Configurar o Ambiente (Só se faz uma vez)

Sempre que começar a trabalhar numa máquina nova (ou clonar o projeto):

```powershell
# 1. Cria a "bolha" venv
python -m venv venv

# 2. Ativa a "bolha"
.\venv\Scripts\Activate.ps1

# 3. Instala a "lista de compras" dentro da bolha
pip install -r requirements.txt

# 4. Copia o "molde" dos segredos
copy config\.env.example config\.env

# 5. ABRA O FICHEIRO 'config/.env' E PREENCHA COM OS SEGREDOS REAIS
```

### 2. Rotina de Trabalho Diária

Sempre que for começar uma nova tarefa:

```powershell
# 1. Ativa a "bolha" (se ainda não estiver ativa)
.\venv\Scripts\Activate.ps1
# (O seu prompt deve agora mostrar (venv) no início)
```

**❗️Alerta Comum do Windows:** Se der um erro vermelho sobre "execução de scripts foi desabilitada", rode este comando uma vez para permitir: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` ...e então tente ativar novamente (`.\venv\Scripts\Activate.ps1`).

Sempre que for **iniciar uma nova tarefa** (ex: criar o `reader.py`):

```powershell
# 1. Vá para a branch principal (o "Documento Final")
git checkout main

# 2. Puxe a versão mais recente do GitHub (dos seus colegas)
git pull origin main

# 3. Crie a sua "cópia de trabalho" (a sua branch)
git checkout -b feature/nome-da-sua-tarefa
# (ex: git checkout -b feature/data-reader)
```

Enquanto está a **trabalhar na sua tarefa**:

```powershell
# --- (Aqui você faz o seu trabalho: cria/edita ficheiros) ---
# ...
# ...

# 4. Veja o que mudou
git status

# 5. Adicione as suas mudanças ao "pacote"
git add .

# 6. Salve o "pacote" (commit) na sua branch
git commit -m "feat: Adiciona o leitor de dados do usuário"

# 7. Envie a sua branch (a sua cópia) para o GitHub
git push -u origin feature/setup-arquitetura ~ exemplooooooo
```

**8. Crie o Pull Request (PR) no GitHub**
* Vá ao site do GitHub.
* Clique em "Compare & pull request".
* Adicione os seus colegas como "Reviewers".
* **É aqui que o trabalho em equipa acontece!**