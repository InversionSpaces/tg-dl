import logging
import asyncio as aio
import signal
import argparse

from tgdl.bot import Bot
from utils.signalwaiter import wait_signals
from config import TOKEN

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', help='Telegram bot token', nargs='?')
    args = parser.parse_args()

    token = args.token or TOKEN

    if token is None:
        logging.error('No token provided')
    else:
        aio.run(main(token))
