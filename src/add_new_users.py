import os
from dotenv import load_dotenv
from tinydb import TinyDB,where


class Controller:
    def __init__(self):
        load_dotenv(override=True)
        
        self.db = TinyDB('admin_panel_db.json')
        self.chat_ids_table = self.db.table('chat_ids')
        self.db_admin = self.db.table('admin')
        self.message = self.db.table('user_message')   
        TARGET_GROUP_ID = os.environ['TARGET_GROUP_ID']
        self.chat_id = int(TARGET_GROUP_ID)

    def add_user(self,message):
        for user in message.new_chat_members:
            payload = self._make_payload(user, action='added')
            user_id = payload['user']['id']
            # Insere se não existir
            if not payload['user']['is_bot']:
                if not self.chat_ids_table.contains(where('chat_id') == user_id):
                    self.chat_ids_table.insert({'chat_id': user_id})   

    def remove_user(self,user):
        payload = self._make_payload(user, action='removed')
        user_id = payload['user']['id']
        
        # Remove se existir
        if self.db_admin.contains(where('chat_id') == user_id):
            self.db_admin.remove(where('chat_id') == user_id)

        # Remove da tabela de admins caso seja admin
        if self.chat_ids_table.contains(where('chat_id') == user_id):
            self.chat_ids_table.remove(where('chat_id') == user_id)

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


