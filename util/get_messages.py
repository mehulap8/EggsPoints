import requests
from datetime import datetime

def get_all_messages(group_id):
    with open('token.txt', 'r') as f:
        token = f.read().strip()

    url = f'https://api.groupme.com/v3/groups/{group_id}/messages'

    params = {
        'token': token,
        'limit': 100
    }

    before_id = None

    while True:
        if before_id:
            params['before_id'] = before_id

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            break

        data = response.json()

        if not data.get('response') or not data['response'].get('messages'):
            break

        messages = data['response']['messages']

        if not messages:
            break

        for msg in messages:
            if msg['text']:
                timestamp = datetime.utcfromtimestamp(msg['created_at']).strftime('%Y-%m-%d %H:%M:%S UTC')
                print(f"[{timestamp}] User ID: {msg['user_id']} | Name: {msg['name']} | Text: {msg['text']}")

        before_id = messages[-1]['id']

if __name__ == '__main__':
    get_all_messages(27967386)
