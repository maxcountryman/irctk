from kaa import Kaa

import urllib
import urlparse
import json

bot = Kaa()
bot.config.from_pyfile('settings.cfg')


@bot.command
def raw(args):
    '''Usage: .raw [command] [args] (admins only)'''
    
    if not bot.irc.context.get('prefix') in bot.config.get('ADMINS'):
        return
    
    if args:
        command = args.split(' ', 1)[0]
        args = list(args.split(' ', 1)[-1])
        bot.irc.send_command(command, args)
    else:
        bot.irc.send_reply(raw.__doc__)

@bot.command('g', threaded=True)
def google(query):
    '''Useage .g [query]'''
    
    if not query:
        return bot.irc.send_reply(google.__doc__)
    
    url = urlparse.urlunsplit(
            (
                'http', 
                'ajax.googleapis.com', 
                '/ajax/services/search/web', 
                'v=1.0&q={0}'.format(query), 
                None,
                )
            )
    
    response = urllib.urlopen(url)
    response = json.loads(response.read())['responseData']['results']
    
    if not response:
        error = 'Request error: no results'
        bot.irc.send_reply(error)
    else:
        url = urllib.unquote(response[0]['url'])
        title = response[0]['titleNoFormatting']
        response = title + ' -- ' + url 
        return bot.irc.send_reply(response)


if __name__ == '__main__':
    bot.run()
