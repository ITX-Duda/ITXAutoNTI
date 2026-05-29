import requests
import urllib3

# Oculta o InsecureRequestWarning do terminal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL correta da API usando o ID 243 do ITXAutoNTI
url = "https://gitlab.ufabc.int.br/api/v4/projects/243/releases"

headers = {
    "PRIVATE-TOKEN": "obiKCmTXjSzHN5TL14Ns", # Lembrete: Revogar este token depois!
    "Content-Type": "application/json"
}

dados = {
    "name": "ITXAutoNTI v1.0.0",
    "tag_name": "v1.0.0",
    "ref": "release/1.0.0",
    "description": """
# 🚀 Release v1.0.0: O Lançamento Oficial do ITXAutoNTI

A versão **1.0.0** do ITXAutoNTI está oficialmente no ar! 🎉

Esta release é um marco histórico para a nossa automação. O que começou como uma iniciativa em um script único amadureceu e se transformou em uma *engine* robusta, orientada a domínio e construída a muitas mãos. Esta versão entrega um robô resiliente, rastreável e pronto para escalar as demandas do GLPI de forma segura. """
}

print("Enviando Release para a API do GitLab...")
resposta = requests.post(url, headers=headers, json=dados, verify=False)

print(f"Status Code: {resposta.status_code}")

if resposta.status_code == 201:
    print("✅ SUCESSO ABSOLUTO! Release criada com sucesso.")
    print("Pode conferir lá na aba de Releases do GitLab!")
else:
    print("❌ Falhou. Detalhes do erro:")
    try:
        print(resposta.json())
    except:
        print(resposta.text)
