from voxbot.bot import Plugin

class Scales(Plugin):
    '''usage: ^scales [key] (lowercase is minor)'''
    
    def __init__(self, bot):
        super(Scales, self).__init__(bot)
        self.notes = {
                0: 'C', 
                1: 'C#', 
                2: 'D', 
                3: 'D#', 
                4: 'E', 
                5: 'F', 
                6: 'F#',
                7: 'G', 
                8: 'G#', 
                9: 'A', 
                10: 'A#', 
                11: 'B'
                }
        self._send_scale()
    
    def find_key(self, _dict, val):
        '''Return the key of dictionary `_dict` given the value'''
        
        return [k for k, v in _dict.iteritems() if v == val][0]
    
    def _gen_scales(self, notes, root):
        major = [2, 2, 1, 2, 2, 2, 1]
        minor = [2, 1, 2, 2, 1, 2, 2]
        root_num = self.find_key(notes, root)
        major_scale = [root]
        minor_scale = [root]
        
        while major:
            root_num += major.pop(0)
            root_num %= 12
            major_scale.append(notes[root_num])
        
        while minor:
            root_num += minor.pop(0)
            root_num %= 12
            minor_scale.append(notes[root_num])
        
        major_scale = ' '.join(major_scale)
        minor_scale = ' '.join(minor_scale)
        return major_scale, minor_scale
    
    @Plugin.command('^scales')
    def _send_scale(self, *args):
        
        inp = args[-1]
        arg = args[-1]
        if arg.upper() in self.notes.values():
            notes = self.notes
            root = arg.upper()
            major_scale, minor_scale = self._gen_scales(notes, root)
            
            if inp == root.lower():
                self.reply(minor_scale)
            else:
                self.reply(major_scale)

