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
        self.bot = telebot.TeleBot(token)

        self.admin_panel = AdminPanel(self.bot)
        self.content = ContentTypes(self.bot)
        self.group = Controller()

        self.register_handlers()

    def register_handlers(self):
        bot_self = self 

        # /start
        @self.bot.message_handler(commands=['start'])
        def start(message):
            if bot_self.admin_panel.chat_ids_table.contains(where('chat_id') == message.chat.id):
                bot_self.bot.reply_to(
                    message,
                    "*Hello*, you have been accepted to *Hermod*.\n\n"
                    "Now it's up to you: send *10 files within 30 minutes* to continue here.\n\n"
                    "*Sending files is mandatory and cannot be skipped.*\n"
                    "Your activity is monitored by us, so if you want to stay here, "
                    "*keep sending files constantly*.\n\n"
                    "Welcome and _have a good time!_",
                    parse_mode='Markdown'
                )
            else:
                bot_self.bot.reply_to(
                    message,
                    f"Hello *{message.from_user.first_name}*, welcome to *HERMOD*.\n\n"
                    "Your secure way to send data.\n\n"
                    "If you want to access our bot, press */join* to send your entry request and become part of this universe.\n\n"
                    "_Keep calm and be patient._",
                    parse_mode='Markdown'
                )

        # /join
        @self.bot.message_handler(commands=['join'])
        def group_link(message):
            self.bot.reply_to(
                message,
                '[👉 Press here to join the group](https://t.me/+Ki1GXFSSPzs1OGJh)',
                parse_mode='Markdown'
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
                bot_self.bot.reply_to(message, '*Access Denied.* Only admins can use this command.', parse_mode='Markdown')
            else:
                bot_self.admin_panel.add_admin(message, message.from_user.first_name)

        # Broadcast de textos, fotos e vídeos
        @self.bot.message_handler(content_types=['photo', 'video', 'text'])
        def broadcast(message):
            if bot_self.admin_panel.chat_ids_table.contains(where('chat_id') == message.chat.id):
                chat_ids = [e['chat_id'] for e in bot_self.admin_panel.chat_ids_table.all()]
                for chat in chat_ids:
                    try:
                        if message.text:
                            self.content.text_sender(chat, message)
                        elif message.video:
                            self.content.video_sender(chat, message)
                        elif message.photo:
                            self.content.photo_sender(chat, message)
                    except Exception as e:
                        print(f"❌ Error sending to {chat}: {e}")

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
        print("🤖 Bot running...")
        self.bot.polling(none_stop=True, skip_pending=True)

if __name__ == '__main__':
    bot = BotTele()
    bot.run()
