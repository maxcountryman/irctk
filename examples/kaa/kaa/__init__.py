from irctk import Bot

from kaa.config import Config

# initialze the bot object
bot = Bot()

# configure the bot object based on a Python class
bot.config.from_object(Config)

# load our plugins
#from kaa import repost
from kaa import (google, python, remember, repost, tell, trolldb,
                 urbandict, utils, weather, wikipedia, youtube)
