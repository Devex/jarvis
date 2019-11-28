import logging
import sys
from slackbot import settings
from slackbot.bot import Bot


def main():
    kw = {
        'format': '[%(asctime)s] %(name)s: %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG if settings.DEBUG else logging.INFO,
        'stream': sys.stdout,
    }
    logging.basicConfig(**kw)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(
        logging.WARNING)
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
