import re
from datetime import datetime
import requests

def load_name_mappings():
    name_to_primary = {}
    primary_to_display = {}

    with open('ids.txt', 'r') as f:
        for line in f:
            match = re.match(r'ID: \d+ \| Name: (.+)', line)
            if match:
                names_str = match.group(1)
                names = [n.strip() for n in names_str.split(',')]
                primary_name = names[0].lower()
                display_name = names[0]

                primary_to_display[primary_name] = display_name
                for name in names:
                    name_to_primary[name.lower()] = primary_name

    return name_to_primary, primary_to_display

def parse_message(text, egg_counts, name_to_primary):
    pattern = r'(\w+(?:\s+\w+)*)\s*(\+\+|--)'
    matches = re.findall(pattern, text)

    for names_str, operator in matches:
        names = [n.lower() for n in names_str.split()]
        delta = 1 if operator == '++' else -1

        for name in names:
            if name in name_to_primary:
                primary_name = name_to_primary[name]
                egg_counts[primary_name] = egg_counts.get(primary_name, 0) + delta

def calculate_egg_counts(group_id):
    with open('token.txt', 'r') as f:
        token = f.read().strip()

    try:
        with open('botUserId.txt', 'r') as f:
            bot_user_id = f.read().strip()
    except FileNotFoundError:
        bot_user_id = None

    name_to_primary, primary_to_display = load_name_mappings()

    url = f'https://api.groupme.com/v3/groups/{group_id}/messages'

    params = {
        'token': token,
        'limit': 100
    }

    before_id = None
    egg_counts = {}
    oldest_timestamp = None
    newest_timestamp = None

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
            if bot_user_id and msg['user_id'] == bot_user_id:
                continue

            if msg['text']:
                timestamp = msg['created_at']
                if oldest_timestamp is None or timestamp < oldest_timestamp:
                    oldest_timestamp = timestamp
                if newest_timestamp is None or timestamp > newest_timestamp:
                    newest_timestamp = timestamp
                parse_message(msg['text'], egg_counts, name_to_primary)

        before_id = messages[-1]['id']

    return {
        'egg_counts': egg_counts,
        'primary_to_display': primary_to_display,
        'oldest_timestamp': oldest_timestamp,
        'newest_timestamp': newest_timestamp
    }

def display_egg_counts(group_id):
    result = calculate_egg_counts(group_id)
    egg_counts = result['egg_counts']
    primary_to_display = result['primary_to_display']

    print("Egg Counts:")
    sorted_eggs = sorted(egg_counts.items(), key=lambda x: x[1], reverse=True)
    for primary_name, count in sorted_eggs:
        display_name = primary_to_display.get(primary_name, primary_name)
        eggs = '🥚' * (count // 50)
        print(f"{display_name}:{eggs} {count}")

if __name__ == '__main__':
    display_egg_counts(27967386)
