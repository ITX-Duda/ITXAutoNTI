import httpx

def autenticarGlpi(api_url, app_token, user_token): #variaveis vindas do .env
    
    cartaoVisita = {
        'App-Token': app_token,
        'Authorization': f'user_token {user_token}', #formata para "user_token xxxxxxxxx"
        'Content-Type': 'application/json', # converte para JSON
    }

    try:
        response = httpx.get(f"{api_url}/initSession", headers=cartaoVisita, verify=False)
        response.raise_for_status()
        session_token = response.json().get('session_token')
        print("✅ Autenticação bem-sucedida.\n")
        return session_token
    except httpx.HTTPStatusError as e:
        print(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Erro inesperado: {e}")     
    return None
