class ContentTypes:
    def __init__(self,bot):
        self.bot = bot

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