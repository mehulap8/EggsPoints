from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
from datetime import datetime
import os
from count_eggs import load_name_mappings, parse_message

app = FastAPI()

GROUP_ID = 27967386

def get_token():
    token = os.getenv('TOKEN')
    if not token:
        raise ValueError("TOKEN environment variable not set")
    return token

def get_bot_id():
    bot_id = os.getenv('BOT_ID')
    if not bot_id:
        raise ValueError("BOT_ID environment variable not set")
    return bot_id

def get_bot_user_id():
    return os.getenv('BOT_USER_ID')

def send_message(text):
    try:
        token = get_token()
        bot_id = get_bot_id()
    except ValueError as e:
        print(f"Error: {e}")
        return False

    url = 'https://api.groupme.com/v3/bots/post'
    payload = {
        'bot_id': bot_id,
        'text': text
    }

    response = requests.post(url, json=payload)
    return response.status_code == 201

def calculate_egg_counts_with_env(group_id):
    try:
        token = get_token()
    except ValueError as e:
        raise e

    bot_user_id = get_bot_user_id()
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

def format_egg_counts():
    result = calculate_egg_counts_with_env(GROUP_ID)
    egg_counts = result['egg_counts']
    primary_to_display = result['primary_to_display']
    oldest_timestamp = result['oldest_timestamp']
    newest_timestamp = result['newest_timestamp']

    lines = []

    if oldest_timestamp is not None:
        oldest = datetime.utcfromtimestamp(oldest_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        newest = datetime.utcfromtimestamp(newest_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        lines.append(f"Oldest: {oldest}")
        lines.append(f"Newest: {newest}")
        lines.append("")

    sorted_eggs = sorted(egg_counts.items(), key=lambda x: x[1], reverse=True)
    for primary_name, count in sorted_eggs:
        display_name = primary_to_display.get(primary_name, primary_name)
        eggs = '🥚' * (count // 50)
        lines.append(f"{display_name}:{eggs} {count}")

    return '\n'.join(lines)

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        print(f"Error parsing request: {e}")
        return JSONResponse({"ok": False}, status_code=400)

    message = data.get('text', '').lower()
    user_id = data.get('user_id')
    bot_user_id = get_bot_user_id()

    if bot_user_id and user_id == bot_user_id:
        return JSONResponse({"ok": True})

    if 'list eggs' in message:
        try:
            egg_list = format_egg_counts()
            send_message(egg_list)
        except Exception as e:
            print(f"Error processing list eggs: {e}")
            send_message(f"Error: {str(e)}")

    return JSONResponse({"ok": True})

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
