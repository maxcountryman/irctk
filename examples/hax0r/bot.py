from irctk import Bot

import urllib
import urlparse
import json

bot = Bot()
bot.config.from_pyfile('settings.cfg')


@bot.command
def raw(context):
    '''usage: .raw <command>'''
    
    if not context.line['prefix'] in bot.config.get('ADMINS'):
        return
    if context.args:
        command = context.args.split(' ', 1)[0]
        args = list(context.args.split(' ', 1)[-1])
        bot.irc.send_command(command, args)
    else:
        return raw.__doc__

@bot.command('g')
@bot.command
def google(context):
    '''Usage .g [query]'''
    
    query = context.args
    if not query:
        return google.__doc__
    
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
        return error
    else:
        url = urllib.unquote(response[0]['url'])
        title = response[0]['titleNoFormatting']
        response = title + ' -- ' + url 
        return response


if __name__ == '__main__':
    bot.run()
