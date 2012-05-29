# import the Bot object from IrcTK
from irctk import Bot

# we'll use these later, install Requests if you don't have it already
import requests
import json

# initlize the bot object
bot = Bot()

# an object container for our configuration values
class Config:
    SERVER = 'irc.voxinfinitus.net'
    PORT = 6697
    SSL = True
    TIMEOUT = 300
    NICK = 'kaa'
    REALNAME = 'kaa the python'
    CHANNELS = ['#testing']

# populate the configuration with our Config object
bot.config.from_object(Config)

# the Google search API URL
search_url = 'http://ajax.googleapis.com/ajax/services/search/web'


@bot.command('g')  # also bind this function to '.g'
@bot.command  # register the wrapped function as a plugin
def google(context):
    # notice that we provide one arg, context: this is optional but if you
    # want access to the IRC line that triggered the plugin you need to
    # pass in some variable; we'll use context for this

    query = context.args  # args are parsed automatically by IrcTK

    # make the request, should give us back some JSON
    r = requests.get(search_url, params=dict(v='1.0', safe='off', q=query))

    # load the JSON
    data = json.loads(r.content)

    # if we don't have results, bail out of the plugin
    if not data['responseData']['results']:
        return 'no results found'

    # otherwise grab the first result
    first_result = data['responseData']['results'][0]

    # build our return string
    ret = first_result['titleNoFormatting'] + ' - ' \
            + first_result['unescapedUrl']

    # finally return the result to the channel or user the plugin was called
    # from
    return ret


if __name__ == '__main__':
    bot.run()
