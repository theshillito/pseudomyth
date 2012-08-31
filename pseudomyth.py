#!/usr/bin/env python
# coding=utf-8

# A script with which to determine what order to watch keions in

from random import choice
from sys import argv
import os
import shutil
import commands
import re
import zenhan

class Series():
    """ A series. Contains episodes. """
    def __init__(self, name):
        self.name = name
        self.episodes = []
        self.op = self.ed = False

    def __repr__(self):
        bonus = ''
        if self.op:
            bonus += 'OP '
        if self.ed:
            bonus += 'ED '
            
        return '%s %r %s' % (self.name, [e.epno for e in self.episodes], bonus)

    def append(self, episode):
        if episode.epno in ['op', 'ed']:
            setattr(self, episode.epno, episode)
        else:
            self.episodes.append(episode)
            self.episodes = sorted(self.episodes, key=lambda episode: episode.epno)

class Episode():
    """ An episode within a series, and its associated file. """
    def __init__(self, filename):
        self.parsed = False
        self.filename = filename
        
        # a horrible workaround for resolving aliases on OS X
        # see http://blog.warrenmoore.net/blog/2010/01/09/make-terminal-follow-aliases-like-symlinks/
        if commands.getstatusoutput('getTrueName')[0] != 32512:
            self.truefilename = commands.getoutput('getTrueName "%s"' % filename)
        else:
            self.truefilename = self.filename
        
        exts = ['mkv', 'avi', 'mp4']
        if not os.path.isdir(filename) and filename.split('.')[-1].lower() in exts:
            self.parse(filename)

    def __repr__(self):
        return '%s - %i' % (self.series, self.epno)

    def parse(self, filename):
        filename = filename.replace('_', ' ')
        
        # remove repeated spaces
        while '  ' in filename:
            filename = filename.replace('  ', ' ')

        # remove metadata (things in brackets)
        metadata = re.findall('[\(\[].*?[\)\]]', filename)
        for m in metadata:
             filename = filename.replace(m, '').strip()

        epno = None
        # regexes for matching episode numbers
        #                01v2                 - 01                 ep( )01                ep. 01                  01
        epno_matches = ['\\b\d+(?=v\d+\\b)', '(?<=\s-\s)\d+\\b', '(?i)(?<=ep) ?\d+\\b', '(?i)(?<=ep\. )\d+\\b', '\\b\d+\\b']
        for regex in epno_matches:
            try:
                epno = int(re.findall(regex, filename)[0])
            except IndexError:
                pass
            else:
                break

        if epno == None:
            # it might be an opening or an ending or an OVA
            op_matches = ['(?i)\\bOP\d*\\b']
            for regex in op_matches:
                if re.search(regex, filename):
                    epno = 'op'

            ed_matches = ['(?i)\\bED\d*\\b']
            for regex in ed_matches:
                if re.search(regex, filename):
                    epno = 'ed'

            one_matches = ['(?i)\\bSpecial\\b', '(?i)\\bOVA\\b']
            for regex in one_matches:
                if re.search(regex, filename):
                    epno = 0
        
        if epno == None:
            # never mind
            print ' :: abandoning parse of', self.filename, 'at episode number'
            return

        series = None
        # regexes for matching series names
        #                 ^bento ep(.)(|)                  ^bento - 0                                        ^bento 0
        series_matches = ['(?i)^.*?(?=\sep\.?\s*\d+\\b)', '(?i)^.*?(?=\s-\s(?=\d+|Special|OVA|OP\d*|ED\d*)\\b)', '(?i)^.*?\s(?=\d|OP\d*\\b|ED\d*\\b|Special|OVA\\b)']
        for regex in series_matches:
            try:
                series = re.findall(regex, filename)[0].strip()
            except IndexError:
                pass
            else:
                break
        
        if series == None:
            print ' :: abandoning parse of', self.filename, 'at series'
            return
        
        self.epno = epno
        self.series = series

        self.parsed = True
        # print '%s - %i %r' % (series, epno, metadata)

if not argv[-1] == 'legacy':
    if not os.path.exists('consumed'):
        os.makedirs('consumed')

    serieslist = []
    
    files = [name for name in os.listdir('.') if not name.startswith('.')]
        
    for filename in files:
        episode = Episode(filename)
        if episode.parsed and episode.series not in [s.name for s in serieslist]:
            series = Series(episode.series)
            series.append(episode)
            serieslist.append(series)

        elif episode.parsed:
            series = [s for s in serieslist if s.name == episode.series][0]
            series.append(episode)
    
    weighted = []
    for series in serieslist:
        for episode in series.episodes:
            weighted.append(series)
    
    total = len(weighted)

    # confirmation
    # full-width numbers are the only reason we need zenhan, so feel free to ditch this bit
    keion_count = zenhan.h2z(unicode(total))

    if total != 1:
        plural = u'Ｓ'
    else:
        plural = ''

    print u'／人◕ ‿‿ ◕人＼  ＬＥＴ’Ｓ　ＷＡＴＣＨ　%s　ＫＥＩＯＮ%s！' % (keion_count, plural)

    for series in sorted(serieslist, key=lambda series: series.name):
        print series

    
    for n in range(len(weighted)):
        issued = raw_input('')
        series = choice(weighted)
        playlist = []
        
        # you can comment out these next two line if you like
        if issued == ' ':
            playlist.append('/Users/nivi/.fim')
            
        series = choice(weighted)

        episode = series.episodes.pop(0)
        weighted.remove(series)
        print '%i/%i - %s' % (n+1, total, episode),

        if series.op:
            playlist.append('"%s"' % series.op.truefilename)
    
        playlist.append('"%s"' % episode.truefilename)

        if series.ed:
            playlist.append('"%s"' % series.ed.truefilename)

        command = 'mplayer -fs %s &> /dev/null' % ' '.join(playlist)
        os.system(command) 

        shutil.move(episode.filename, 'consumed/%s' % episode.filename)

else:
    # manual series entry for when the above bullshit inevitably breaks
    showlist = []

    while True:
        newkeion = raw_input('')
        if newkeion == '':
            break
        else:
            showlist.append(newkeion)

    # showlist.append('strike witches')

    total = len(showlist)
    n = 1

    for n in range(len(showlist)):
        nextshow = choice(showlist)
        print '%i/%i - %s' % (n+1, total, nextshow),
        showlist.remove(nextshow)
        raw_input('')