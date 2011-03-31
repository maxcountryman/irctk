class redditradio(object):
    
    def __init__(self, bot):
        self.bot = bot
        self.msgs = self.bot.line['args'][-1]
        self.sender = self.bot.line['args'][0]
        self.user = self.bot.line['prefix'].split('!')[0]
        self._np()
        self._np_rock()
        self._np_electronic()
        self._np_hiphop()
        self._status()
        self._status_rock()
        self._status_electronic()
        self._status_hiphop()
        self._status_main()
        self._info()
    
    def _np(self):
        import urllib, json
        if '^np' == self.msgs:
            json_results = \
                    urllib.urlopen('http://radioreddit.com/api/status.json')
            _results = json.loads(json_results.read())
            results = _results['songs']['song'][0]['title'] \
                    + ' by ' + \
                    _results['songs']['song'][0]['artist']
            if not self.sender == self.bot.nick:
                self.bot.msg(self.sender, 'Now playing on Radio Reddit: ' + results)
            else:
                self.bot.reply(self.user, 'Now playing on Radio Reddit: ' + results)

    def _np_rock(self):
        import urllib, json
        if '^np rock' == self.msgs:
            json_results = \
                    urllib.urlopen('http://radioreddit.com/api/rock/status.json')
            _results = json.loads(json_results.read())
            results = _results['songs']['song'][0]['title'] \
                    + ' -- ' + \
                    _results['songs']['song'][0]['artist']
            if not self.sender == self.bot.nick:
                self.bot.msg(self.sender, 'Now playing on the rock stream: ' + results)
            else:
                self.bot.reply(self.user, 'Now playing on the rock stream: ' + results)

    def _np_electronic(self):
        import urllib, json
        if '^np electronic' == self.msgs:
            json_results = \
                    urllib.urlopen('http://radioreddit.com/api/electronic/status.json')
            _results = json.loads(json_results.read())
            results = _results['songs']['song'][0]['title'] \
                    + ' -- ' + \
                    _results['songs']['song'][0]['artist']
            if not self.sender == self.bot.nick:
                self.bot.msg(self.sender, 'Now playing on the electronic stream: ' + results)
            else:
                self.bot.reply(self.user, 'Now playing on the electronic stream: ' + results)
    
    def _np_hiphop(self):
        import urllib, json
        if '^np hiphop' == self.msgs:
            json_results = \
                    urllib.urlopen('http://radioreddit.com/api/hiphop/status.json')
            _results = json.loads(json_results.read())
            results = _results['songs']['song'][0]['title'] \
                    + ' -- ' + \
                    _results['songs']['song'][0]['artist']
            if not self.sender == self.bot.nick:
                self.bot.msg(self.sender, 'Now playing on the hip-hop stream: ' + results)
            else:
                self.bot.reply(self.user, 'Now playing on the hip-hop stream: ' + results)
    
    def _status(self):
        import urllib, json
        if '^status' == self.msgs:
            main_results = \
                    urllib.urlopen('http://radioreddit.com/api/status.json')
            rock_results = \
                    urllib.urlopen('http://radioreddit.com/api/rock/status.json')
            electronic_results = \
                    urllib.urlopen('http://radioreddit.com/api/electronic/status.json')
            hiphop_results = \
                    urllib.urlopen('http://radioreddit.com/api/hiphop/status.json')
            main_results = json.loads(main_results.read())
            rock_results = json.loads(rock_results.read())
            electronic_results = json.loads(electronic_results.read())
            hiphop_results = json.loads(hiphop_results.read())
            results = int(main_results['listeners']) + int(rock_results['listeners']) + int(electronic_results['listeners']) + int(hiphop_results['listeners'])
            if not self.sender == self.bot.nick:
                self.bot.msg(self.sender, 'There are {0} listeners currently'.format(results))
            else:
                self.bot.reply(self.user, 'There are {0} listeners currently'.format(results))

    def _status_rock(self):
        import urllib, json
        if '^status rock' == self.msgs:
            json_results = \
                    urllib.urlopen('http://radioreddit.com/api/rock/status.json')
            _results = json.loads(json_results.read())
            results = _results['listeners']
            if not self.sender == self.bot.nick:
                self.bot.msg(self.sender, 'There are {0} listeners currently'.format(results))
            else:
                self.bot.reply(self.user, 'There are {0} listeners currently'.format(results))

    def _status_electronic(self):
        import urllib, json
        if '^status electronic' == self.msgs:
            json_results = \
                    urllib.urlopen('http://radioreddit.com/api/electronic/status.json')
            _results = json.loads(json_results.read())
            results = _results['listeners']
            if not self.sender == self.bot.nick:
                self.bot.msg(self.sender, 'There are {0} listeners currently'.format(results))
            else:
                self.bot.reply(self.user, 'There are {0} listeners currently'.format(results))

    def _status_hiphop(self):
        import urllib, json
        if '^status hiphop' == self.msgs:
            json_results = \
                    urllib.urlopen('http://radioreddit.com/api/hiphop/status.json')
            _results = json.loads(json_results.read())
            results = _results['listeners']
            if not self.sender == self.bot.nick:
                self.bot.msg(self.sender, 'There are {0} listeners currently'.format(results))
            else:
                self.bot.reply(self.user, 'There are {0} listeners currently'.format(results))

    def _status_main(self):
        import urllib, json
        if '^status main' == self.msgs:
            json_results = \
                    urllib.urlopen('http://radioreddit.com/api/status.json')
            _results = json.loads(json_results.read())
            results = _results['listeners']
            if not self.sender == self.bot.nick:
                self.bot.msg(self.sender, 'There are {0} listeners currently'.format(results))
            else:
                self.bot.reply(self.user, 'There are {0} listeners currently'.format(results))
    
    def _info(self):
        if '^info' == self.msgs:
            if not self.sender == self.bot.nick:
                self.bot.msg(self.sender, 'Radio Reddit information: http://radioreddit.com/about, http://radioreddit.com/faq')
            else:
                self.bot.reply(self.user,  'Radio Reddit information: http://radioreddit.com/about, http://radioreddit.com/faq')
                
