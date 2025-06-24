import telebot
import os
class Verificator:
    
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)

        # Handler para qualquer mensagem recebida
        @self.bot.message_handler(func=lambda message: True)
        def handle_message(message):
            if message.chat.type in ["group", "supergroup"]:
                print(f"ID do grupo: {message.chat.id}")

    def run(self):
        self.bot.polling()

# Exemplo de uso:
if __name__ == "__main__":
    token = os.getenv('TOKEN')
    bot = Verificator(token)
    bot.run()
