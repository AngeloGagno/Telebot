import os
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
        self.bot = telebot.TeleBot(token, parse_mode='HTML') 

        # Instâncias das outras classes
        self.admin_panel = AdminPanel(self.bot)
        self.content = ContentTypes(self.bot)
        self.group = Controller()

        # Registrar todos os handlers
        self.register_handlers()

    def register_handlers(self):
        bot_self = self 

        # /start
        @self.bot.message_handler(commands=['start'])
        def start(message):
            if bot_self.admin_panel.chat_ids_table.contains(where('chat_id') == message.chat.id):
                bot_self.bot.reply_to(
                    message,
                    "<b>Hello</b>, you have been accepted to <b>Hermod</b>.<br><br>"
                    "Now it's up to you: send <b>10 files within 30 minutes</b> to continue here.<br><br>"
                    "<b>Sending files is mandatory and cannot be skipped.</b><br>"
                    "Your activity is monitored by us, so if you want to stay here, "
                    "<b>keep sending files constantly</b>.<br><br>"
                    "Welcome and <i>have a good time!</i>."
                )
            else:
                bot_self.bot.reply_to(
                    message,
                    f"Hello <b>{message.from_user.first_name}</b>, welcome to <b>HERMOD</b>.<br><br>"
                    "Your secure way to send data.<br><br>"
                    "If you want to access our bot, press <b>/join</b> to send your entry request and become part of this universe.<br><br>"
                    "<i>Keep calm and be patient.</i>"
                )

        # /join
        @self.bot.message_handler(commands=['join'])
        def group_link(message):
            self.bot.reply_to(
                message,
                '<a href="https://t.me/+Ki1GXFSSPzs1OGJh"> Press here to join the group</a>'
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
                bot_self.bot.reply_to(message, ' Access Denied. Only admins can use this command.')
            else:
                bot_self.admin_panel.add_admin(message, message.from_user.first_name)

        # Broadcast de texto, foto e vídeo
        @self.bot.message_handler(content_types=['photo', 'video', 'text'])
        def broadcast(message):
            if bot_self.admin_panel.chat_ids_table.contains(where('chat_id') == message.chat.id):
                chat_ids = [e['chat_id'] for e in bot_self.admin_panel.chat_ids_table.all()]
                for chat in chat_ids:
                    if message.text:
                        self.content.text_sender(chat, message)
                    elif message.video:
                        self.content.video_sender(chat, message)
                    elif message.photo:
                        self.content.photo_sender(chat, message)

        # Novo membro no grupo
        @self.bot.message_handler(content_types=['new_chat_members'])
        def on_user_added(message):
            self.group.add_user(message)

        # Membro saiu
        @self.bot.message_handler(content_types=['left_chat_member'])
        def on_user_removed(message):
            user = message.left_chat_member
            self.group.remove_user(user=user)

    def run(self):
        self.bot.polling()

if __name__ == '__main__':
    bot = BotTele()
    bot.run()
