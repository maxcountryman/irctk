from voxbot.bot import Plugin

import time

TIMEOUT = 0.0009

class Bf(Plugin):
    '''usage: ^bf [brainfuck]'''
    
    def __init__(self, bot):
        super(Bf, self).__init__(bot)
        self._send_response()
    
    @Plugin.command('^bf')
    def _send_response(self, *args, **kwargs):
            bf = kwargs.get('args', '')
            bf = self._parse(bf)
            if bf:
                self.reply(bf)
            else:
                self.reply('Parser timeout')
    
    def _parse(self, raw):
        
        tape = [0] * 30000 # thirty-thousand cells
        cell = 0
        loopstack = []
        
        output = ''
        
        start = time.time()
        pointer = 0
        while pointer < len(raw):
            instr = raw[pointer]
            
            if time.time() - start >= TIMEOUT:
                return None
            
            if instr == '>':
                cell += 1
            elif instr == '<':
                cell -= 1
            elif instr == '+':
                tape[cell] += 1
            elif instr == '-':
                tape[cell] -= 1
            elif instr == '.':
                output += chr(tape[cell])
            elif instr == '[':
                loopstack.insert(0, pointer)
            elif instr == ']':
                loop = loopstack.pop(0)
                if tape[cell] != 0:
                    pointer = loop
                    loopstack.insert(0, loop)
            
            pointer += 1
        
        return output

