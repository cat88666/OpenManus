import requests
import time

TOKEN = "8330652586:AAEwEv1R46T6Iw3aBlGO7HUmdbzwezVrNTs"

def get_chat_id():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    print("Waiting for a message to your bot... Please send a message to your bot now.")
    for _ in range(10):
        try:
            response = requests.get(url).json()
            if response.get("result"):
                chat_id = response["result"][-1]["message"]["chat"]["id"]
                print(f"Found Chat ID: {chat_id}")
                return chat_id
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(3)
    print("Could not find Chat ID. Did you send a message to the bot?")
    return None

if __name__ == "__main__":
    get_chat_id()
