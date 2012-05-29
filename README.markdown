##IrcTK

IrcTK is a little IRC framework for developing IRC-based applications.

##Features

* Simple, intuitive API
* Automatic reloading
* Multithreaded


##Installation

Install the package with one of the following commands:

    $ easy_install irctk

or

    $ pip install irctk

##Example Usage

Using IrcTK is easy and fun. If you've ever used a framework like Flask you
probably already know what to do.

Let's write a simple bot that queries Google when it sees the command
'.google'. We'll start by configuring our application:

```python
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
    CHANNELS = ['#voxinfinitus']

# populate the configuration with our Config object
bot.config.from_object(Config)
```

Now that our bot is setup and configured we can get to the fun part: writing
plugins for it!

Plugins in IrcTK are functions that are registered via a decorator. For our bot
we want to write a function that queries Google and gives us the first result.

```python
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
```

And that's it! You've just written your first plugin. There's one more thing we
need to do and then your bot is ready to roll:

```python
# run our bot
if __name__ == '__main__':
    bot.run()
```

That's how simple and easy it is to write IRC applications with IrcTK. The
[complete example](https://github.com/maxcountryman/irctk/tree/master/examples/google.py)
is available in the examples directory. Also a [more complete example bot](https://github.com/maxcountryman/irctk/tree/master/examples/kaa)
is available there as well.
