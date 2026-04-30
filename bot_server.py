from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import os
import re
from count_eggs import load_name_mappings, parse_message
from database import init_db, update_count, get_all_counts

app = FastAPI()

GROUP_ID = 27967386

@app.on_event("startup")
async def startup_event():
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Could not initialize database on startup: {e}")

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

def process_message_for_counts(text):
    """Extract ++ and -- patterns and update database"""
    name_to_primary, _ = load_name_mappings()

    pattern = r'(\w+(?:\s+\w+)*)\s*(\+\+|--)'
    matches = re.findall(pattern, text)

    for names_str, operator in matches:
        names = [n.lower() for n in names_str.split()]
        delta = 1 if operator == '++' else -1

        for name in names:
            if name in name_to_primary:
                primary_name = name_to_primary[name]
                try:
                    update_count(primary_name, delta)
                except Exception as e:
                    print(f"Error updating count for {primary_name}: {e}")

def format_egg_counts():
    name_to_primary, primary_to_display = load_name_mappings()

    try:
        egg_counts = get_all_counts()
    except Exception as e:
        print(f"Error fetching counts from database: {e}")
        return f"Error: Could not fetch egg counts ({str(e)})"

    if not egg_counts:
        return "No egg counts yet!"

    lines = []
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

    text = data.get('text', '')
    if text:
        process_message_for_counts(text)

    if 'list eggs' in message.lower():
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
