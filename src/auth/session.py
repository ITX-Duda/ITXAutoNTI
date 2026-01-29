import httpx

def autenticar_glpi(api_url, app_token, user_token):
    
    headers = {
        'App-Token': app_token,
        'Authorization': f'user_token {user_token}',
        'Content-Type': 'application/json',
    }

    try:
        # verify=False é perigoso em produção, mas OK para homologação
        response = httpx.get(f"{api_url}/initSession", headers=headers, verify=False)
        response.raise_for_status()
        session_token = response.json().get('session_token')
        print("Autenticação bem-sucedida.\n")
        return session_token
    except httpx.HTTPStatusError as e:
        print(f"Erro HTTP: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Erro inesperado: {e}")     
    return None