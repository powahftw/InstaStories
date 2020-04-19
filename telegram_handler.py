import telegram
from logging import Handler

class TelegramHandler(Handler):

    DISABLE_NOTIFICATION = True
    MAX_MESSAGE_LENGTH = telegram.constants.MAX_MESSAGE_LENGTH

    def __init__(self, api_key, chat_id):
        Handler.__init__(self)
        self.bot = telegram.Bot(token=api_key)
        self.chat_id = chat_id
        self.curr_buffer_size = 0
        self.logs_buffer = []

    def emit(self, record):
        formatted_log = self.format(record)
        if len(formatted_log) + self.curr_buffer_size >= self.MAX_MESSAGE_LENGTH:
            self.send_buffered_data()
        self.logs_buffer.append(formatted_log)
        self.curr_buffer_size += len(formatted_log) + 1  # +1 to account for newline

    def send_buffered_data(self):
        msg = '\n'.join(self.logs_buffer)
        self.bot.send_message(self.chat_id, msg, disable_notification=self.DISABLE_NOTIFICATION)
        self.curr_buffer_size = 0
        self.logs_buffer = []
