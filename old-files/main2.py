import requests
TOKEN = "6021312829:AAGai0OKbxdoyBJSXGOeKDA-8gpU6WyZN8c"
chat_id = "@connectforum"
message = "rgegdfgd"
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
print(requests.get(url).json()) # Эта строка отсылает сообщение