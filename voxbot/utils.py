import htmllib
import bitly_api

def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

def rainbowify(s,shift=2):
    return ''.join(map(lambda x: chr(3) + str(x[0]+shift) + ',' + str(x[0]) + x[1], enumerate(s)))
    
bitly = bitly_api.Connection(
        'voxinfinitus', 
        'R_d3664470e5404623b5c0e3a25a873286', 
        )

