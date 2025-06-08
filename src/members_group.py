import os
import json
from dotenv import load_dotenv
from tinydb import TinyDB, Query
import telebot

class ChatIDVerify:
    def __init__(self):
        load_dotenv(override=True)
        
        self.db = TinyDB('admin_panel_db.json')
        self.chat_ids_table = self.db.table('chat_ids')

        TARGET_GROUP_ID = os.environ['TARGET_GROUP_ID']
        self.chat_id = int(TARGET_GROUP_ID)

        token = os.environ['TOKEN']
        self.bot = telebot.TeleBot(token)

        self.register_handlers()

    def register_handlers(self):
        # Quando alguém for adicionado
        @self.bot.message_handler(content_types=['new_chat_members'])
        def on_user_added(message):
            for user in message.new_chat_members:
                payload = self.make_payload(user, action='added')
                user_id = payload['user']['id']

                # só insere se ainda não existir
                if not self.chat_ids_table.contains(Query().chat_id == user_id):
                    self.chat_ids_table.insert({'chat_id': user_id})
                    # se quiser ver no console:
                    print(json.dumps(payload, indent=2, ensure_ascii=False))

        # Quando alguém sair ou for removido
        @self.bot.message_handler(content_types=['left_chat_member'])
        def on_user_removed(message):
            user = message.left_chat_member
            payload = self.make_payload(user, action='removed')
            user_id = payload['user']['id']

            # só remove se existir
            if self.chat_ids_table.contains(Query().chat_id == user_id):
                self.chat_ids_table.remove(Query().chat_id == user_id)
                print(json.dumps(payload, indent=2, ensure_ascii=False))

    def make_payload(self, user, action):
        user_dict = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'is_bot': user.is_bot
        }
        return {
            'action': action,   # 'added' ou 'removed'
            'user': user_dict
        }

    def polling(self):
        self.bot.polling()

if __name__ == '__main__':
    verifier = ChatIDVerify()
    verifier.polling()

