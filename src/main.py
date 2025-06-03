import os
import telebot
import json
from dotenv import load_dotenv


class BotTele:
    def __init__(self):

        load_dotenv(override=True)
        token = os.environ['TOKEN']
        self.admin_ids = json.loads(os.environ.get('ADMINS', '[]')) 

        self.bot = telebot.TeleBot(token)
        self.chat_ids_file = 'chat_ids.json'
        self.pending_file = 'pending_chat_ids.json'

        self.chat_ids = self.load_chat_ids()
        self.pending = self.load_pending()

        self.register_handlers()

    def register_handlers(self):
        '''Faz o tratamento das mensagem do usuario'''
        @self.bot.message_handler(commands=['start'])
        def start(message):
            '''Inicia a aplicação'''
            if message.chat.id in self.chat_ids:
                self.bot.reply_to(message, f'Bem vindo - {message.from_user.first_name}, envie fotos, textos ou vídeos para fazer broadcast')
            else:
                self.add_pending(message.chat.id, message.from_user.first_name)
                self.bot.reply_to(message, 'Você não possui cadastro. Sua solicitação foi enviada ao admin para aprovação.')
        @self.bot.message_handler(commands=['admin'])
        def admin_panel(message):
            if message.chat.id not in self.admin_ids:
                return self.bot.reply_to(message, 'Acesso negado. Somente admins podem usar esse comando.')

            text = "Painel de Admin:\nPendentes:\n"
            if not self.pending:
                text += "Nenhum pendente."
            else:
                for p in self.pending:
                    text += f"ID: {p['chat_id']} - Nome: {p['username']}\n"
                text += "\nUse /approve <chat_id> para aprovar."

            self.bot.reply_to(message, text)

        @self.bot.message_handler(commands=['approve'])
        def approve_user(message):
            if message.chat.id not in self.admin_ids:
                return self.bot.reply_to(message, 'Acesso negado.')

            try:
                chat_id = int(message.text.split()[1])
            except (IndexError, ValueError):
                return self.bot.reply_to(message, 'Uso correto: /approve <chat_id>')

            pending_user = next((p for p in self.pending if p['chat_id'] == chat_id), None)
            if pending_user:
                self.chat_ids.append(chat_id)
                self.save_chat_ids()
                self.pending = [p for p in self.pending if p['chat_id'] != chat_id]
                self.save_pending()
                self.bot.reply_to(message, f'Usuário {pending_user["username"]} aprovado.')
                self.bot.send_message(chat_id, 'Sua solicitação foi aprovada. Você agora pode enviar mensagens.')
            else:
                self.bot.reply_to(message, 'Usuário não encontrado na lista de pendentes.')

        @self.bot.message_handler(content_types=['photo', 'video', 'text'])
        def broadcast(message):
            '''Verifica o ID e caso seja permitido, o broadcast será feito'''
            if message.chat.id in self.chat_ids:
                for chat in self.chat_ids:
                    if message.text:
                        self.text_sender(chat, message)
                    if message.video:
                        self.video_sender(chat, message)
                    if message.photo:
                        self.photo_sender(chat, message)



    def add_pending(self, chat_id, username):
        if not any(p['chat_id'] == chat_id for p in self.pending):
            self.pending.append({'chat_id': chat_id, 'username': username})
            self.save_pending()

    def load_chat_ids(self):
        if os.path.exists(self.chat_ids_file):
            with open(self.chat_ids_file, 'r') as f:
                return json.load(f)
        return []

    def save_chat_ids(self):
        with open(self.chat_ids_file, 'w') as f:
            json.dump(self.chat_ids, f)

    def load_pending(self):
        if os.path.exists(self.pending_file):
            with open(self.pending_file, 'r') as f:
                return json.load(f)
        return []

    def save_pending(self):
        with open(self.pending_file, 'w') as f:
            json.dump(self.pending, f)

    def text_sender(self, chat, message):
        return self.bot.send_message(chat, f'#{message.from_user.first_name}: {message.text}')
    
    def video_sender(self, chat, message):
        video_file_id = message.video.file_id 
        return self.bot.send_video(chat, video_file_id)
    
    def photo_sender(self, chat, message):
        photo_file_id = message.photo[-1].file_id 
        return self.bot.send_photo(chat, photo_file_id)    

    def run(self):
        print("Bot rodando...")
        self.bot.polling()

if __name__ == '__main__':
    bot = BotTele()
    bot.run()
