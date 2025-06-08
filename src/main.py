import os
import json
from dotenv import load_dotenv
import telebot
from tinydb import where
from admin import AdminPanel
from add_new_users import Controller
from senders import ContentTypes

class BotTele:
    def __init__(self):
        load_dotenv(override=True)
        token = os.environ['TOKEN']
        self.bot = telebot.TeleBot(token)
        
        # Instancia AdminPanel com o mesmo bot e prepara o DB de chat_ids
        self.admin_panel = AdminPanel(self.bot)

        # Instancia ContentTypes onde contem os tratadores de mensagem
        self.content = ContentTypes(self.bot)

        # Instancia de ação do grupo 
        self.group = Controller()
        # Registrar os handlers de comandos, broadcast e eventos de membros
        self.register_handlers()

    def register_handlers(self):
        """Faz o tratamento dos comandos e eventos do bot"""
        bot_self = self 

        # /start
        @self.bot.message_handler(commands=['start'])
        def start(message):
            if bot_self.admin_panel.chat_ids_table.contains(where('chat_id') == message.chat.id):
                bot_self.bot.reply_to(
                    message,
                    f'Bem-vindo - {message.from_user.first_name}, envie fotos, textos ou vídeos para fazer broadcast'
                )
            else:
                bot_self.bot.reply_to(
                    message,
                    'Você não possui cadastro. Caso deseje acessar o bot envie mensagem para .'
                )

        # /admin
        @self.bot.message_handler(commands=['admin'])
        def admin_command(message):
            bot_self.admin_panel.admin_panel(message)

        # /new_admin
        @self.bot.message_handler(commands=['new_admin'])
        def create_admin(message):
            if len(bot_self.admin_panel.db_admin) == 0:
                bot_self.admin_panel.add_admin(message, message.from_user.first_name)
                return
            if not bot_self.admin_panel.db_admin.contains(where('chat_id') == message.chat.id):
                bot_self.bot.reply_to(message, 'Acesso negado. Somente admins podem adicionar novos admins.')
            else:
                bot_self.admin_panel.add_admin(message, message.from_user.first_name)

        # Broadcast de textos, fotos e vídeos
        @self.bot.message_handler(content_types=['photo', 'video', 'text'])
        def broadcast(message):
            if bot_self.admin_panel.chat_ids_table.contains(where('chat_id') == message.chat.id):
                chat_ids = [e['chat_id'] for e in bot_self.admin_panel.chat_ids_table.all()]
                for chat in chat_ids:
                    if message.text:
                        self.content.text_sender(chat, message)
                    if message.video:
                        self.content.video_sender(chat, message)
                    if message.photo:
                        self.content.photo_sender(chat, message)

        # Quando alguém for adicionado ao grupo
        @self.bot.message_handler(content_types=['new_chat_members'])
        def on_user_added(message):
            self.group.add_user(message)            

        # Quando alguém sair ou for removido do grupo
        @self.bot.message_handler(content_types=['left_chat_member'])
        def on_user_removed(message):
            user = message.left_chat_member
            self.group.remove_user(user=user)

    def run(self):
        print("Bot rodando...")
        self.bot.polling()

if __name__ == '__main__':
    bot = BotTele()
    bot.run()

