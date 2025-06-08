import os
import json
from tinydb import TinyDB, Query

class AdminPanel:
    def __init__(self, bot):
        self.bot = bot
        # Inicializa banco TinyDB
        self.db = TinyDB('admin_panel_db.json')
        self.chat_ids_table = self.db.table('chat_ids')
        self.db_admin = self.db.table('admin')

    def add_admin(self,message,username):
        
        if len(self.db_admin) == 0:

            self.db_admin.insert({'chat_id':message.chat.id,'promoted_by':username})
            self.verify_user_admin(chat_id=message.chat.id)

        else:
            self.admin_verificator(message)
            try:
                chat_id = int(message.text.split()[1])
            except (IndexError, ValueError):
                return self.bot.reply_to(message, 'Uso correto: /approve <chat_id>')
            
            self.verify_user_admin(chat_id)

            self.db_admin.insert({'chat_id':chat_id,'promoted_by':username})
            self.bot.reply_to(message,'Admin Inserido com sucesso.')

    def verify_user_admin(self,chat_id):
        User = Query()
        if not self.chat_ids_table.contains(User.chat_id == chat_id):
            self.chat_ids_table.insert({'chat_id':chat_id})

    def admin_panel(self,message):
        self.admin_verificator(message)
        
        text = 'Painel de Admin:\n' \
        'Para verificar se há pendentes: /pending\n' \
        'Para remover um usuario: /remove ' 
        self.bot.reply_to(message, text)

    def admin_verificator(self, message):
        User = Query()
        if not self.db_admin.contains(User.chat_id == message.chat.id):
            return self.bot.reply_to(message, 'Acesso negado. Somente admins podem usar esse comando.')



