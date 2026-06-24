<div align="center">

# 🤖 ITXAutoNTI
**Intelligent Task Automation for GLPI**

<p align="center">
  <img src="https://img.shields.io/badge/Release-v1.1.0-success?style=for-the-badge&logo=rocket" alt="Release" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge&logo=mit" alt="License" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
</p>

<p align="center">
  <a href="./README.pt-br.md"><img src="https://img.shields.io/badge/🇧🇷_Português-grey?style=flat-square" alt="Português"/></a>
  <a href="./README.fr.md"><img src="https://img.shields.io/badge/🇫🇷_Français-grey?style=flat-square" alt="Français"/></a>
</p>

> *Turning hours of manual work into milliseconds of efficiency with RPA and API integrations.*

</div>

---

## 📖 Overview

**ITXAutoNTI** is an automation robot designed to interact natively with GLPI. It reads instructions, interprets complex logic, and executes automated actions on the platform — such as batch-linking multiple assets to a ticket or intelligently closing tasks.

Originally developed at the **NTI (Information Technology Center) of UFABC** (Federal University of ABC, Brazil), the tool is built to be replicable by any Federal Higher Education Institution (IFES) or organization running GLPI.

---

## 🧠 System Architecture

The processing pipeline is divided into four independent modules running in sequence:

<div align="center">

| <img src="https://img.icons8.com/neon/96/code-fork.png" width="48px" alt="Module 1"><br>1. Retriever | ➡️ | <img src="https://img.icons8.com/neon/96/brain.png" width="48px" alt="Module 2"><br>2. Parser | ➡️ | <img src="https://img.icons8.com/neon/96/api.png" width="48px" alt="Module 3"><br>3. Executor | ➡️ | <img src="https://img.icons8.com/neon/96/checked.png" width="48px" alt="Module 4"><br>4. Closer |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fetches** active tasks | | **Parses** the logic | | **Executes** via API | | **Closes** and logs |

</div>

---

## ✨ Key Features

* 📚 **Intelligent Reading:** The robot reads and understands tasks exactly as the analyst wrote them.
* 📦 **Batch Execution:** Capable of linking multiple assets to a ticket simultaneously.
* ⚡ **Direct API Communication:** Performs all operations directly via GLPI's REST API (fast and transparent).
* 🦡 **Automatic Reply:** Automatically replies to the ticket confirming the operation's success.
* 📊 **Audit Trail:** Automatically attaches `ITX_Relatorio.csv` with detailed logs and action statuses.
* 🎯 **Location Fuzzy Matching:** AI-powered algorithm that intelligently corrects and maps location names entered with typos, using the institution's internal data dictionary.

---

## 🚀 Getting Started

Follow the steps below to set up your environment and run the project locally:

### 📋 Prerequisites
* **Python 3.8+** installed.
* **Git** for cloning the repository.
* Access credentials for the **GLPI API**.

### ⚙️ Installation

**1. Clone the repository:**
```bash
git clone https://github.com/ITX-Duda/ITXAutoNTI.git
cd ITXAutoNTI
```

**2. Create and activate a virtual environment (Recommended):**
```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Configure security keys and environment:**
Create or edit the `.env` file (inside the `config/` folder) and add the following **required** GLPI API credentials:
```env
GLPI_API_URL="https://your-glpi-instance/apirest.php"
GLPI_APP_TOKEN="your_app_token_from_glpi"
GLPI_USER_TOKEN="your_user_token_from_glpi"
```
> **⚠️ Note on Fuzzy Matching (Private File):**
> The location correction engine requires a file named `localizacao.csv` in the `src/logic/` folder. Because it contains the internal infrastructure mapping of the institution, **this file is confidential and is not part of the public repository**. Anyone deploying this application must generate and provide their own CSV file with their institution's internal locations.

**5. Start the engine:**
```bash
python main.py
```

---

## 📄 Scientific Publication

This project was presented at **WTIFICES 2026** (Workshop on Undergraduate Work in Computer Science and Systems, CSBC 2026) and documented in the following scientific paper:

> **Automation and Optimization of IT Processes at UFABC: The Development and Implementation of ITXAutoNTI**
> M. E. A. B. Brito, E. F. Lima, B. B. Bianchi, P. H. de Lima Franca, F. D. C. Iglesias
> *Workshop de Trabalhos de Iniciação em Computação e Sistemas (WTIFICES), CSBC 2026*

📎 [Full paper (PDF)](./Artigo_WTIFICES_ITXAutoNTI.pdf)

---

## 👨‍💻 Authors

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

## ⚖️ Intellectual Property & Licensing

**Intellectual Property Notice:**
The source code, architecture, design, and logic of **ITXAutoNTI** constitute intellectual property developed by the team listed above. This repository reflects the official `v1.1.0` release for formal registration and authorship documentation purposes.

**Rights Notice:**
© 2026 ITXAutoNTI Team.
All rights reserved. Any use, modification, or distribution of parts or the entirety of this software must comply with the conditions established in the applicable licensing model for this repository.

---

## 🙏 Credits & References

| Project | Usage in ITXAutoNTI |
|---|---|
| [giovanny07/python-glpi-utils](https://github.com/giovanny07/python-glpi-utils) | Architectural reference for implementing dynamic API pagination (overcoming GLPI's native 50-item limit) |
| [rapidfuzz/RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) | Fuzzy matching engine for intelligent location correction |
| [encode/httpx](https://github.com/encode/httpx) | Modern HTTP client for stable API communication |

---

<p align="center">
  <img src="https://img.icons8.com/neon/96/bot.png" width="32px" alt="bot"><br>
  <b>Built by the ITXAutoNTI Team!</b><br>
</p>
