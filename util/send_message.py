import requests
import sys

def send_message(message):
    with open('token.txt', 'r') as f:
        token = f.read().strip()

    with open('botId.txt', 'r') as f:
        bot_id = f.read().strip()

    url = 'https://api.groupme.com/v3/bots/post'

    payload = {
        'bot_id': bot_id,
        'text': message
    }

    response = requests.post(url, json=payload)

    if response.status_code == 201:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python send_message.py <message>")
        sys.exit(1)

    message = ' '.join(sys.argv[1:])
    send_message(message)
