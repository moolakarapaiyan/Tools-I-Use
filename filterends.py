#this code copied from @m4llok tool - https://github.com/m4ll0k/Bug-Bounty-Toolz/blob/master/collector.py
#we can filter unnecessary endpoints from a file
#!/usr/bin/python3
#cat endpoints.txt | filterends

import sys,html
from urllib import parse
from html import unescape
import re
import os

blacklist = [
r'^application/\w+',
r'^audio/\w+',
r'^text/\w+',
r'^image/\w+',
r'^video/\w+',
r'^\./',
r'^M/d/y',
r'^M/d/yy',
r'y/M/d',
r'y/MM/dd',
r'd/M/y',
r'dd/MM/yy',
r'^\.\./',
r'^chemical/\w+',
r'^conference/\w+',
r'^x-www-form-urlencoded',
r'^message/\w+',
r'^model/\w+',
r'\.jpg|\.jpeg|\.gif|\.css|\.tif|\.tiff|\.png|\.ttf|\.woff|\.woff2|\.ico|\.pdf|\.svg',
r'^//about:blank'
]

def main(url):
        url = unescape(parse.unquote(url))

        if not re.search('|'.join(blacklist),url,re.I):
            
            if len(url) >= 150:
                pass
            else:
                print(url)

for i in sys.stdin.readlines():
        i = i.strip()
        main(i)
