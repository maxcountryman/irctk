from irctk import Bot

from kaa.config import Config

# initialze the bot object
bot = Bot()

# configure the bot object based on a Python class
bot.config.from_object(Config)

# load our plugins
from kaa import (google, imdb, python, remember, repost, tell, urbandict,
        utils, weather, wikipedia, youtube)
