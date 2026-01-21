import httpx

def userName(api_url, app_token, user_token, session_token):
    headers = {
        'App-Token': app_token,
        'Authorization': f'user_token {user_token}',
        'Content-Type': 'application/json',
        'Session-Token': session_token
    }

    with httpx.Client(verify=False) as client: 
        response = client.get(f"{api_url}/user/39160", headers=headers)
    
        if response.status_code == 200:
            usuario = response.json().get('firstname')
            print("Usuário encontrado:")
            print(usuario)
        else:
            print("Erro:", response.status_code, response.text)
