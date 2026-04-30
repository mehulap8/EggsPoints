from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
from datetime import datetime
import os
from count_eggs import calculate_egg_counts

app = FastAPI()

GROUP_ID = 27967386

def get_bot_id():
    try:
        with open('botId.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def get_bot_user_id():
    try:
        with open('botUserId.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def send_message(text):
    try:
        with open('token.txt', 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        print("Error: token.txt not found")
        return False

    bot_id = get_bot_id()
    if not bot_id:
        print("Error: botId.txt not found")
        return False

    url = 'https://api.groupme.com/v3/bots/post'
    payload = {
        'bot_id': bot_id,
        'text': text
    }

    response = requests.post(url, json=payload)
    return response.status_code == 201

def format_egg_counts():
    result = calculate_egg_counts(GROUP_ID)
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
