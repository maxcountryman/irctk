class Config(object):
    
    SETTINGS = {
    'server': 'irc.voxinfinitus.net', 
    'nick': 'Kaa', 
    'realname': 'Kaa the Python', 
    'port': 6697, 
    'ssl': True, 
    'channels': [
        '#testing',
        '#voxinfinitus',
        '#radioreddit',
        '#techsupport'
        ],
    'plugins': [
        'Debug', 
        'Google', 
        'Radioreddit', 
        'Bitly', 
        'Raw', 
        'Python', 
        'Imdb',
        'Scales',
        'Bf',
        'Action'
        ],
    'owners': ['doraemon']
    }

