import requests

def get_group_members():
    with open('token.txt', 'r') as f:
        token = f.read().strip()

    with open('groupId.txt', 'r') as f:
        group_id = f.read().strip()

    url = f'https://api.groupme.com/v3/groups/{group_id}'

    params = {
        'token': token
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return

    data = response.json()

    if not data.get('response') or not data['response'].get('members'):
        print("No members found")
        return

    members = data['response']['members']

    for member in members:
        print(f"ID: {member['user_id']} | Name: {member['nickname']}")

if __name__ == '__main__':
    get_group_members()
