<div align="center">

# 🤖 ITXAutoNTI
**Automatisation Intelligente des Tâches dans GLPI**

<p align="center">
  <img src="https://img.shields.io/badge/Release-v1.1.0-success?style=for-the-badge&logo=rocket" alt="Release" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge&logo=mit" alt="Licence" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
</p>

<p align="center">
  <a href="./README.md"><img src="https://img.shields.io/badge/🇺🇸_English-grey?style=flat-square" alt="English"/></a>
  <a href="./README.pt-br.md"><img src="https://img.shields.io/badge/🇧🇷_Português-grey?style=flat-square" alt="Português"/></a>
</p>

> *Transformer des heures de travail manuel en millisecondes d'efficacité grâce au RPA et aux intégrations via API.*

</div>

---

## 📖 Vue d'ensemble

**ITXAutoNTI** est un robot d'automatisation conçu pour interagir nativement avec GLPI. Il lit des instructions, interprète des logiques complexes et exécute des actions automatisées sur la plateforme — comme l'association en lot de plusieurs équipements à un ticket ou la clôture intelligente de tâches.

Développé à l'origine au **NTI (Núcleo de Tecnologia da Informação) de l'UFABC** (Université Fédérale de l'ABC, Brésil), l'outil a été conçu pour être réplicable par toute institution utilisant GLPI.

---

## 🧠 Architecture du Système

Le pipeline de traitement est divisé en quatre modules indépendants fonctionnant en séquence :

<div align="center">

| <img src="https://img.icons8.com/neon/96/code-fork.png" width="48px" alt="Module 1"><br>1. Retriever | ➡️ | <img src="https://img.icons8.com/neon/96/brain.png" width="48px" alt="Module 2"><br>2. Parser | ➡️ | <img src="https://img.icons8.com/neon/96/api.png" width="48px" alt="Module 3"><br>3. Executor | ➡️ | <img src="https://img.icons8.com/neon/96/checked.png" width="48px" alt="Module 4"><br>4. Closer |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Récupère** les tâches actives | | **Analyse** la logique | | **Exécute** via l'API | | **Clôture** et journalise |

</div>

---

## ✨ Fonctionnalités Principales

* 📚 **Lecture Intelligente :** Le robot lit et comprend la tâche exactement telle qu'elle a été rédigée par le technicien.
* 📦 **Exécution en Lot :** Capacité d'associer plusieurs équipements à un ticket simultanément.
* ⚡ **Communication Directe via API :** Toutes les opérations sont effectuées directement via l'API REST de GLPI (rapide et transparent).
* 🦡 **Réponse Automatique :** Répond automatiquement au ticket en confirmant le succès de l'opération.
* 📊 **Audit et Historique :** Attache automatiquement le fichier `ITX_Relatorio.csv` avec les journaux détaillés et les statuts des actions.
* 🎯 **Correspondance Approximative des Localisations :** Algorithme d'IA qui corrige et mappe intelligemment les noms de lieux saisis avec des fautes de frappe.

---

## 🚀 Démarrage Rapide

### 📋 Prérequis
* **Python 3.8+**, **Git** et les identifiants d'accès à l'**API GLPI**.

### ⚙️ Installation

**1. Cloner le dépôt :**
```bash
git clone https://github.com/ITX-Duda/ITXAutoNTI.git
cd ITXAutoNTI
```

**2. Créer et activer un environnement virtuel (Recommandé) :**
```bash
# Sur Windows
python -m venv venv
.\venv\Scripts\activate

# Sur Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**3. Installer les dépendances :**
```bash
pip install -r requirements.txt
```

**4. Configurer les clés de sécurité et l'environnement :**
Créez ou modifiez le fichier `.env` (dans le dossier `config/`) et ajoutez les identifiants GLPI **obligatoires** :
```env
GLPI_API_URL="https://votre-instance-glpi/apirest.php"
GLPI_APP_TOKEN="votre_app_token_glpi"
GLPI_USER_TOKEN="votre_user_token_glpi"
```

> **⚠️ Note sur la Correspondance Approximative (Fichier Privé) :**
> Le moteur de correction de localisation nécessite un fichier `localizacao.csv` dans le dossier `src/logic/`. Ce fichier contient la cartographie interne de l'infrastructure de l'institution et **n'est pas inclus dans le dépôt public**. Toute institution souhaitant déployer l'application doit générer et fournir son propre fichier CSV avec ses localisations internes.

**5. Lancer le moteur :**
```bash
python main.py
```

---

## 📄 Publication Scientifique

Ce projet a été présenté au **WTIFICES 2026** (Workshop de Trabalhos de Iniciação em Computação e Sistemas, CSBC 2026) et documenté dans l'article scientifique suivant :

> **Automatisation et Optimisation des Processus IT à l'UFABC : Le Développement et l'Implémentation d'ITXAutoNTI**
> M. E. A. B. Brito, E. F. Lima, B. B. Bianchi, P. H. de Lima Franca, F. D. C. Iglesias
> *Workshop de Trabalhos de Iniciação em Computação e Sistemas (WTIFICES), CSBC 2026*

📎 [Article complet (PDF)](./Artigo_WTIFICES_ITXAutoNTI.pdf)

---

## 👨‍💻 Auteurs

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

## ⚖️ Propriété Intellectuelle et Licence

**Avis de Propriété Intellectuelle :**
Le code source, l'architecture, le design et la logique d'**ITXAutoNTI** constituent la propriété intellectuelle de l'équipe citée ci-dessus. Ce dépôt reflète la version officielle `v1.1.0` à des fins d'enregistrement formel et de documentation d'auteur.

**Avis de Droits :**
© 2026 Équipe ITXAutoNTI.
Tous droits réservés. Toute utilisation, modification ou distribution de tout ou partie de ce logiciel doit respecter les conditions établies dans le modèle de licence applicable à ce dépôt.

---

## 🙏 Crédits et Références

| Projet | Utilisation dans ITXAutoNTI |
|---|---|
| [giovanny07/python-glpi-utils](https://github.com/giovanny07/python-glpi-utils) | Référence architecturale pour la pagination dynamique de l'API GLPI (dépassement de la limite native de 50 éléments) |
| [rapidfuzz/RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) | Moteur de correspondance approximative pour la correction intelligente des localisations |
| [encode/httpx](https://github.com/encode/httpx) | Client HTTP moderne pour une communication stable avec l'API |

---

<p align="center">
  <img src="https://img.icons8.com/neon/96/bot.png" width="32px" alt="bot"><br>
  <b>Développé par l'Équipe ITXAutoNTI !</b><br>
</p>
