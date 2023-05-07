import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from tgdl.downloader import ImageDownloader, ImageDownloadError
from tgdl.converter import ImageConverter


class Bot:
    def __init__(self, token):
        self.downloader = ImageDownloader()
        self.app = ApplicationBuilder().token(token).build()
        self.converter = ImageConverter()

    async def __aenter__(self):
        await self.downloader.__aenter__()
        await self.app.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.downloader.__aexit__(*args)
        await self.app.__aexit__(*args)

    def register_handlers(self):
        start_handler = CommandHandler('start', self.start_handler)
        url_handler = MessageHandler(
            filters.TEXT &
            (~ filters.COMMAND) &
            (~ filters.UpdateType.EDITED) &
            filters.Entity('url'),
            self.url_handler)
        default_handler = MessageHandler(filters.ALL, self.default_handler)

        self.app.add_handler(start_handler)
        self.app.add_handler(url_handler)
        self.app.add_handler(default_handler)

        self.app.add_error_handler(self.error_handler)

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Send me URL to image or video and I'll download it for you."
        )

    async def url_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        for entity in update.message.entities:
            if entity.type != 'url':
                continue

            url = update.message.text[entity.offset:entity.offset + entity.length]

            try:
                name, type = await self.downloader.download_image(url)

                if type not in ['jpeg', 'png', 'gif']:
                    # TODO: Can file become bigger after conversion?
                    self.converter.convert(name, 'png')

                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=name
                )
            except ImageDownloadError as e:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Error: {e}"
                )

    async def default_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Unrecognized message, please try again."
        )

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        logging.error(msg="Exception while handling an update:",
                      exc_info=context.error)

    async def start(self):
        self.register_handlers()
        await self.app.start()
        await self.app.updater.start_polling()

    async def stop(self):
        await self.app.updater.stop()
        await self.app.stop()
