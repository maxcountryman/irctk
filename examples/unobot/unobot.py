from irctk import Bot

import time
import random

bot = Bot()
bot.config.from_pyfile('settings.cfg')

def create_deck():
    red_cards = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9'] * 2 + ['r0']
    blue_cards = ['b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9'] * 2 + ['b0']
    yellow_cards = ['y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8', 'y9'] * 2 + ['y0']
    green_cards = ['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'g9'] * 2 + ['g0']
    action_cards = ['rs', 'rr', 'rd2'] * 2 + ['bs', 'br', 'bd2'] * 2 + ['ys', 'yr', 'yd2'] * 2 + ['gs', 'gr', 'gd2'] * 2
    wild_cards = ['w'] * 4 + ['wd4'] * 4
    
    deck = (red_cards + blue_cards + yellow_cards + green_cards + action_cards 
            + wild_cards)
    random.shuffle(deck)
    
    return deck

def get_card_name(identifier):
    card_mapper = { 
            'r0': 'Red 0',
            'r1': 'Red 1',
            'r2': 'Red 2',
            'r3': 'Red 3',
            'r4': 'Red 4',
            'r5': 'Red 5',
            'r6': 'Red 6',
            'r7': 'Red 7',
            'r8': 'Red 8',
            'r9': 'Red 9',
            'rr': 'Red Reverse',
            'rs': 'Red Skip',
            'rd2': 'Red Draw 2',
            'b0': 'Blue 0',
            'b1': 'Blue 1',
            'b2': 'Blue 2',
            'b3': 'Blue 3',
            'b4': 'Blue 4',
            'b5': 'Blue 5',
            'b6': 'Blue 6',
            'b7': 'Blue 7',
            'b8': 'Blue 8',
            'b9': 'Blue 9',
            'br': 'Blue Reverse',
            'bs': 'Blue Skip',
            'bd2': 'Blue Draw 2',
            'y0': 'Yellow 0',
            'y1': 'Yellow 1',
            'y2': 'Yellow 2',
            'y3': 'Yellow 3',
            'y4': 'Yellow 4',
            'y5': 'Yellow 5',
            'y6': 'Yellow 6',
            'y7': 'Yellow 7',
            'y8': 'Yellow 8',
            'y9': 'Yellow 9',
            'yr': 'Yellow Reverse',
            'ys': 'Yellow Skip',
            'yd2': 'Yellow Draw 2',
            'g0': 'Green 0',
            'g1': 'Green 1',
            'g2': 'Green 2',
            'g3': 'Green 3',
            'g4': 'Green 4',
            'g5': 'Green 5',
            'g6': 'Green 6',
            'g7': 'Green 7',
            'g8': 'Green 8',
            'g9': 'Green 9',
            'gr': 'Green Reverse',
            'gs': 'Green Skip',
            'gd2': 'Green Draw 2',
            }
    return card_mapper[identifier]

@bot.command('start')
def start_uno(context):
    start_time = time.time()
    end = 15.0
    time_up = False
    players = []
    bot._send_reply('Uno game starting. Type .join to play!', context.line)
    while not time_up:
        if time.time() - start_time >= end:
            time_up = True
            if not players:
                return 'times up! no players'
            else:
                bot._send_reply('players: ' + ' '.join(players), context.line)
                deck = create_deck()
                discard = deck.pop(0)
                bot._send_reply('Current discard is: ' + get_card_name(discard), context.line)
                # start game
        if ('.join' in bot.irc.context['message']) and not bot.irc.context['user'] in players:
            user = bot.irc.context['user']
            players.append(user)
            bot._send_reply('{0} joined the game'.format(user), context.line)

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

if __name__ == '__main__':
    bot.run()
