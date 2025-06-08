import os
import json
from dotenv import load_dotenv
import telebot
from tinydb import where
from admin import AdminPanel

class BotTele:
    def __init__(self):
        load_dotenv(override=True)
        token = os.environ['TOKEN']
        self.bot = telebot.TeleBot(token)
        
        # Instancia AdminPanel com o mesmo bot e prepara o DB de chat_ids
        self.admin_panel = AdminPanel(self.bot)

        # Registrar os handlers de comandos, broadcast e eventos de membros
        self.register_handlers()

    def register_handlers(self):
        """Faz o tratamento dos comandos e eventos do bot"""
        bot_self = self  # Captura 'self' para uso dentro dos handlers

        # /start
        @self.bot.message_handler(commands=['start'])
        def start(message):
            if bot_self.admin_panel.chat_ids_table.contains(where('chat_id') == message.chat.id):
                bot_self.bot.reply_to(
                    message,
                    f'Bem-vindo - {message.from_user.first_name}, envie fotos, textos ou vídeos para fazer broadcast'
                )
            else:
                bot_self.admin_panel.add_pending(message.chat.id, message.from_user.first_name)
                bot_self.bot.reply_to(
                    message,
                    'Você não possui cadastro. Sua solicitação foi enviada ao admin para aprovação.'
                )

        # /admin
        @self.bot.message_handler(commands=['admin'])
        def admin_command(message):
            bot_self.admin_panel.admin_panel(message)

        # /pending
        @self.bot.message_handler(commands=['pending'])
        def pending_command(message):
            bot_self.admin_panel.pending_panel(message)

        # /approve
        @self.bot.message_handler(commands=['approve'])
        def approve_command(message):
            bot_self.admin_panel.approve_users(message)

        # /remove
        @self.bot.message_handler(commands=['remove'])
        def remove_command(message):
            bot_self.admin_panel.remove_users(message)

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
                        bot_self.text_sender(chat, message)
                    if message.video:
                        bot_self.video_sender(chat, message)
                    if message.photo:
                        bot_self.photo_sender(chat, message)

        # Quando alguém for adicionado ao grupo
        @self.bot.message_handler(content_types=['new_chat_members'])
        def on_user_added(message):
            for user in message.new_chat_members:
                payload = bot_self._make_payload(user, action='added')
                user_id = payload['user']['id']
                # Insere se não existir
                if not bot_self.admin_panel.chat_ids_table.contains(where('chat_id') == user_id):
                    bot_self.admin_panel.chat_ids_table.insert({'chat_id': user_id})
                    print(json.dumps(payload, indent=2, ensure_ascii=False))

        # Quando alguém sair ou for removido do grupo
        @self.bot.message_handler(content_types=['left_chat_member'])
        def on_user_removed(message):
            user = message.left_chat_member
            payload = bot_self._make_payload(user, action='removed')
            user_id = payload['user']['id']
            # Remove se existir
            if bot_self.admin_panel.chat_ids_table.contains(where('chat_id') == user_id):
                bot_self.admin_panel.chat_ids_table.remove(where('chat_id') == user_id)
                

    def _make_payload(self, user, action):
        """Gera o payload dict para adição ou remoção de usuário"""
        user_dict = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'is_bot': user.is_bot
        }
        return {
            'action': action,
            'user': user_dict
        }

    def caption(self, message):
        return f'Sended_by: {message}'

    def text_sender(self, chat, message):
        self.bot.send_message(chat, f'#{message.from_user.first_name}: {message.text}')

    def video_sender(self, chat, message):
        caption = self.caption(message=message.from_user.first_name)
        video_file_id = message.video.file_id
        self.bot.send_video(chat, video_file_id, caption=caption)

    def photo_sender(self, chat, message):
        caption = self.caption(message=message.from_user.first_name)
        photo_file_id = message.photo[-1].file_id
        self.bot.send_photo(chat, photo_file_id, caption)

    def run(self):
        print("Bot rodando...")
        self.bot.polling()

if __name__ == '__main__':
    bot = BotTele()
    bot.run()

