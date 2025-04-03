import requests
from datetime import datetime

class TelegramNotifier():
    def __init__(self, bot_token, chat_id):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = str(chat_id)  # Convertiamo in stringa per sicurezza
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/"

    def _escape_markdown(self, text):
        """Escape dei caratteri speciali per MarkdownV2"""
        escape_chars = '_*[]()~`>#+-=|{}.!\\'
        return ''.join(f'\\{char}' if char in escape_chars else char for char in str(text))

    def _send_api_request(self, method, payload):
        """Metodo interno per gestire le richieste API"""
        try:
            response = requests.post(self.base_url + method, data=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Errore API Telegram: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nDettagli: {e.response.text}"
            print(error_msg)
            return None

    def send_message(self, text, parse_mode="MarkdownV2"):
        """Versione più robusta del metodo send_message"""
        # Pulizia del testo e encoding
        text = self._escape_markdown(text)
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }

        result = self._send_api_request("sendMessage", payload)

        if result is None:
            print("Fallback: provo a inviare senza Markdown...")
            payload['parse_mode'] = None
            return self._send_api_request("sendMessage", payload) is not None

        return True

    def send_task_notification(self, task_data):
        """Versione migliorata con migliore gestione degli errori"""
        required_fields = ["PROJECT", "TASK", "OWNER", "STATUS", "DATE", "NOTE"]
        if not all(field in task_data for field in required_fields):
            print("Errore: Dati task mancanti o incompleti")
            return False

        try:
            task_date = datetime.strptime(task_data["DATE"], "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            task_date = self._escape_markdown(task_data["DATE"])

        status_emoji = {
            "DONE": "✅",
            "IN PROGRESS": "🔄",
            "TODO": "📝",
            "BLOCKED": "⛔",
            "FAILED": "❌"
        }.get(task_data["STATUS"].upper(), "🔹")

        message = f"""
📌 TASK REMINDER
─────────────────
🏷️ Project: `{self._escape_markdown(task_data['PROJECT'])}`
📋 Task: `{self._escape_markdown(task_data['TASK'])}`
👤 Owner: `{self._escape_markdown(task_data['OWNER'])}`
📅 Date: `{task_date}`
📊 Status: {status_emoji} `{self._escape_markdown(task_data['STATUS'])}`
─────────────────
📝 Notes: {self._escape_markdown(task_data['NOTE'])}
─────────────────
#TaskReminder #{self._escape_markdown(task_data['PROJECT'].replace(' ', ''))} #{self._escape_markdown(task_data['STATUS'].replace(' ', ''))}
"""
        return self.send_message(message)


# Esempio di utilizzo con gestione errori avanzata
if __name__ == "__main__":
    # Configurazione
    BOT_TOKEN = ""  # Sostituisci con il tuo token reale
    CHAT_ID = ""  # Sostituisci con il tuo chat ID reale

    notifier = TelegramNotifier(BOT_TOKEN, CHAT_ID)

    # Test di connessione semplice
    print("Test di connessione al bot...")
    test_payload = {'chat_id': CHAT_ID, 'text': 'Test di connessione'}
    test_result = notifier._send_api_request("getMe", {})

    if test_result is None:
        print("❌ Connessione fallita. Verifica:")
        print(f"1. Il token del bot è corretto? (Iniziare con 'bot'?)")
        print(f"2. Il chat ID è corretto? (Per gruppi, inizia con -100)")
        print(f"3. Il bot è stato aggiunto al gruppo/canale?")
        print(f"4. Hai bloccato il bot per caso?")
    else:
        print("✅ Connessione riuscita!")
        print(f"Bot name: {test_result.get('result', {}).get('first_name', '')}")

        # Invio notifica di esempio
        task_info = {
            "PROJECT": "Website Redesign",
            "TASK": "Implement new header (v2.0)",
            "OWNER": "Mario Rossi",
            "STATUS": "DONE",
            "DATE": "2025-03-26",
            "NOTE": "Completed all responsive versions\n- Approved by UX team\n- Ready for production deploy"
        }

        print("\nInvio notifica task...")
        if notifier.send_task_notification(task_info):
            print("✅ Notifica inviata con successo!")
        else:
            print("❌ Fallito l'invio della notifica")
