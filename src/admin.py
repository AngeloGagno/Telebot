import os
import json
from tinydb import TinyDB, Query

class AdminPanel:
    def __init__(self, bot):
        self.bot = bot
        # Inicializa banco TinyDB
        self.db = TinyDB('admin_panel_db.json')
        self.chat_ids_table = self.db.table('chat_ids')
        self.pending_table = self.db.table('pending')
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

    def pending_panel(self, message):
        self.admin_verificator(message)
        text = "Painel para aprovação:\nPendentes:\n"

        pending = self.pending_table.all()

        if not pending:
            text += "Nenhum pendente."
        else:
            for p in pending:
                text += f"ID: {p['chat_id']} - Nome: {p['username']}\n"
            text += "\nUse /approve <chat_id> para aprovar."

        self.bot.reply_to(message, text)

    def approve_users(self, message):
        User = Query()
        if not self.db_admin.contains(User.chat_id == message.chat.id):
            return self.bot.reply_to(message, 'Acesso negado.')

        try:
            chat_id = int(message.text.split()[1])
        except (IndexError, ValueError):
            return self.bot.reply_to(message, 'Uso correto: /approve <chat_id>')

        pending_user = self.pending_table.get(User.chat_id == chat_id)

        if pending_user:
            self.chat_ids_table.insert({'chat_id': chat_id})
            self.pending_table.remove(User.chat_id == chat_id)

            self.bot.reply_to(message, f'Usuário {pending_user["username"]} aprovado.')
            self.bot.send_message(chat_id, 'Sua solicitação foi aprovada. Você agora pode enviar mensagens.')
        else:
            self.bot.reply_to(message, 'Usuário não encontrado na lista de pendentes.')

    def remove_users(self, message):
        self.admin_verificator(message)
        try:
            chat_id = int(message.text.split()[1])
        except (IndexError, ValueError):
            return self.bot.reply_to(message, 'Uso correto: /remove <chat_id>')

        User = Query()
        if self.chat_ids_table.contains(User.chat_id == chat_id):
            self.chat_ids_table.remove(User.chat_id == chat_id)
            self.bot.reply_to(message, f'Usuário {chat_id} removido com sucesso.')
        else:
            self.bot.reply_to(message, 'Usuário não encontrado.')

    def admin_verificator(self, message):
        User = Query()
        if not self.db_admin.contains(User.chat_id == message.chat.id):
            return self.bot.reply_to(message, 'Acesso negado. Somente admins podem usar esse comando.')


    def add_pending(self, chat_id, username):
        User = Query()
        if not self.pending_table.contains(User.chat_id == chat_id):
            self.pending_table.insert({'chat_id': chat_id, 'username': username})


