import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import asyncio as aio
import signal
import os

from tgdl.bot import Bot
from utils.signalwaiter import wait_signals

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def main(token):
    async with Bot(token) as bot:
        await bot.start()
        await wait_signals(signal.SIGINT, signal.SIGTERM)
        await bot.stop()


if __name__ == '__main__':
    token = os.environ.get('TOKEN')
    if token is None:
        logging.error('TOKEN environment variable is not set')
    else:
        aio.run(main(token))
