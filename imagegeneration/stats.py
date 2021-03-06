from dataretrieval import stats
from utils import integers, times, strings
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import asyncio
import aiohttp
import random
from io import BytesIO
import logging

LOGGER = logging.getLogger('stats_generation')

DEFAULT_SIZE = (1000,600)
DEFAULT_FONT = 'assets/burbank.ttf'
DEFAULT_FONT_NEAT = 'assets/bitstream-bold.ttf'
DEFAULT_COLOR = (255,255,255,170)

class Background:
    def __init__(self,color=None,url=None):
        if (color == None and url == None) or (color != None and url != None):
            raise RuntimeError('You must specify either color or url not both or neither.')
        if color != None:
            self.color = color
        elif url != None:
            self.url = url
        self.size = DEFAULT_SIZE
    @property
    def color(self):
        return self._color
    @color.setter
    def color(self,color):
        self._color = color
        self._url = None
    @property
    def url(self):
        return self._url
    @url.setter
    def url(self,url):
        self._url = url
        self._color = None
    @asyncio.coroutine
    def generate(self):
        image = None
        if self.color != None:
            image = PIL.Image.new('RGBA',self.size,color=self.color)
        elif self.url != None:
            image = yield from self.collectImage(self.url)
            image = yield from self.reCropImage(image,self.size)
        return image
    @staticmethod
    @asyncio.coroutine
    def collectImage(url):
        session = aiohttp.ClientSession()
        response = yield from session.get(url)
        content = yield from response.read()
        response.close()
        yield from session.close()
        image = PIL.Image.open(BytesIO(content)).convert('RGBA')
        return image
    @staticmethod
    @asyncio.coroutine
    def reCropImage(image,size):
        if image.height / size[1] > image.width / size[0]:
            width = size[0]
            height = round(size[1] / image.width * image.height)
            image = image.resize((width,height))
            top = (height - size[1])/2
            bottom = height - top
            image = image.crop((0,top,width,bottom))
        elif image.width / size[0] > image.height / size[1]:
            height = size[1]
            width = round(size[0] / image.height * image.width)
            image = image.resize((width,height))
            left = (width - size[0])/2
            right = width - left
            image = image.crop((left,0,right,height))
        elif image.width / size[0] == image.height / size[1]:
            image = image.resize(size)
        return image

class Overlay:
    def __init__(self,color=None,cs=False):
        self.size = DEFAULT_SIZE
        if color == None:
            self.color = DEFAULT_COLOR
        else:
            self.color = color
        self.currentSeason = cs
    @asyncio.coroutine
    def generate(self,data):
        image = PIL.Image.new('RGBA',self.size,(0,0,0,0))
        padding_x = round(self.size[0]/20)
        padding_y = round(self.size[1]/20)
        size_x_small = padding_x*5
        size_x_large = padding_x*12
        size_y_small = padding_y*5
        size_y_large = padding_y*12
        overview = Overview((size_x_large,size_y_small))
        overview_image = yield from overview.generate(data, self.currentSeason)
        image.paste(overview_image,(padding_x,padding_y),overview_image)
        performance = Performance((size_x_small,size_y_small))
        performance_image = yield from performance.generate(data)
        image.paste(performance_image,(padding_x*2+size_x_large,padding_y),performance_image)
        main = Main((size_x_small+size_x_large+padding_x,size_y_large))
        main_image = yield from main.generate(data, self.currentSeason)
        image.paste(main_image,(padding_x,padding_y*2+size_y_small),main_image)
        return image

class Overview:
    def __init__(self,size):
        self.size = size
        self.color = DEFAULT_COLOR
        self.padding = 15
    @asyncio.coroutine
    def generate(self,data, cs):
        userdata = data.userdata
        stats = data.lifetime
        statsmap = Map(stats,True)
        image = PIL.Image.new('RGBA',self.size,self.color)
        draw = PIL.ImageDraw.Draw(image)
        fontsize = round(self.size[1]/2)-self.padding*2
        font = PIL.ImageFont.truetype(DEFAULT_FONT,size=fontsize)
        font_small = PIL.ImageFont.truetype(DEFAULT_FONT,size=round(fontsize/2))
        draw.text((self.padding,self.padding),userdata.name,fill=(255,255,255,255),font=font)
        statstext = 'KD {kd} | WINS {wins} | WIN% {win_percent}'.format_map(statsmap)
        draw.text((self.padding,fontsize+self.padding*3),statstext,fill=(255,255,255,255),font=font)
        extra = 'MATCHES {matches}\nSCORE {score}'.format_map(statsmap)
        extrasize = font_small.getsize(extra.split('\n')[0])
        extrasizewidth = integers.max(extrasize[0],font_small.getsize(extra.split('\n')[1])[0])
        extrasize = (extrasizewidth,extrasize[1]*2 + 5)
        extraleft = self.size[0]-(extrasize[0]+self.padding)
        extratop = self.padding
        draw.multiline_text((extraleft,extratop),extra,fill=(255,255,255,255),font=font_small,spacing=5)
        platformsize = font.getsize(userdata.platform)[0]
        platformleft = extraleft-(self.padding+platformsize)
        draw.text((platformleft,self.padding),userdata.platform,fill=(255,255,255,255),font=font)
        return image

class Performance:
    def __init__(self,size):
        self.size = size
        self.color = DEFAULT_COLOR
        self.padding = 20
    @asyncio.coroutine
    def generate(self,data):
        matches = data.matches
        lifetime_matches = int(data.lifetime.matches)
        image = PIL.Image.new('RGBA',self.size,self.color)
        draw = PIL.ImageDraw.Draw(image)
        fontsize = round(self.padding/3*2)
        font = PIL.ImageFont.truetype(DEFAULT_FONT_NEAT,size=fontsize)
        fg = (255,255,255,255)
        draw.line([(self.padding,self.padding),(self.padding,self.size[1]-self.padding)],fill=fg,width=2)
        draw.line([(self.padding,self.size[1]-self.padding),(self.size[0]-self.padding,self.size[1]-self.padding)],fill=fg,width=2)
        text_top = round(self.size[1]-self.padding/4)
        self.centeredText(draw,font,'KD',horizontal=round((self.padding-font.getsize('KD')[0])/2),vertical=True,fill=fg)
        intervals = len(matches)
        kds = []
        match_count = 0
        for match in matches:
            kds.append(match.kd)
            match_count += match.matches
        first_match = lifetime_matches - match_count
        self.centeredText(draw,font,'Last {} matches'.format(match_count),horizontal=True,vertical=round(text_top-font.getsize('Mins')[1]),fill=fg)
        lowest = integers.lowest(*kds)
        highest = integers.highest(*kds)
        if lowest is None:
            lowest = 0
        else:
            lowest = round(integers.lowest(*kds),1)
        if highest is None:
            highest = 1
        else:
            highest = round(integers.highest(*kds),1)
        if intervals > 0:
            matches.reverse()
            matches_real = []
            match_id = first_match
            for match in matches:
                for i in range(1,match.matches+1):
                    matches_real.append(MatchEssential(match_id+i,match.kd))
                match_id += match.matches
            range_kd = highest-lowest
            total_size = self.size[0]-self.padding*2
            interval_size = round(total_size/(match_count+2))
            left = self.padding+interval_size
            bottom = self.size[1]-self.padding-5
            height = self.size[1]-self.padding*2-5
            last_pos = None
            now = times.epoch_now()/60
            for i in range(1,len(matches_real)+1):
                if i-2 > 0:
                    last_no = matches_real[i-2].kd
                else:
                    last_no = -1
                if i < len(matches_real):
                    next_no = matches_real[i].kd
                else:
                    next_no = -1
                match = matches_real[i-1]
                if range_kd < 0.1:
                    range_kd = 0.1
                size_y = (match.kd-lowest)*(height/range_kd)
                pos = (left,round(bottom-size_y))
                tl = (pos[0]-2,pos[1]-2)
                br = (pos[0]+2,pos[1]+2)
                if match.kd != last_no or match.kd != next_no:
                    draw.ellipse([tl,br],fill=fg)
                last_no = match.kd
                if last_pos != None:
                    draw.line([last_pos,pos],fill=fg,width=2)
                match_id = str(match.match)
                width = font.getsize(match_id)[0]
                if i == 1 or i == match_count:
                    draw.text((round(left-width/2),round(text_top-font.getsize('0')[1])),match_id,fill=fg,font=font)
                last_pos = pos
                left += interval_size
            lowest = strings.strDec(lowest)
            highest = strings.strDec(highest)
            LOGGER.debug('Performance highest: %s lowest: %s', highest, lowest)
            left = round((self.padding-font.getsize(lowest)[0])/2)
            top = round(self.size[1]-self.padding-5-(font.getsize(lowest)[1]/2))
            draw.text((left, top), lowest, font=font, fill=fg)
            left = round((self.padding-font.getsize(highest)[0])/2)
            top = round(self.padding-(font.getsize(highest)[1]/2))
            draw.text((left, top), highest, font=font, fill=fg)
        return image
    def centeredText(self,draw,font,text,horizontal=True,vertical=True,**textargs):
        if horizontal == True:
            left = round((self.size[0]-font.getsize(text)[0])/2)
        else:
            left = horizontal
        if vertical == True:
            top = round((self.size[1]-font.getsize(text)[1])/2)
        else:
            top = vertical
        draw.text((left,top),text,font=font,**textargs)

class Main:
    def __init__(self,size):
        self.size = size
        self.color = (0,0,0,0)
        self.padding = 15
    @asyncio.coroutine
    def generate(self,data,cs=False):
        stats = data.stats
        image = PIL.Image.new('RGBA',self.size,self.color)
        draw = PIL.ImageDraw.Draw(image)
        font = PIL.ImageFont.truetype(DEFAULT_FONT_NEAT,size=24)
        fg = (255,255,255,255)
        columnsize = round(self.size[0]/7)
        rowsize = round(self.size[1]/4)
        draw.rectangle([(4,4),(columnsize-4,rowsize-4)],fill=DEFAULT_COLOR)
        if cs:
            rows = ['curr_SOLO','curr_DUO','curr_SQUAD']
            toptext = 'Current'
            bottext = 'season'
            sizetop = font.getsize(toptext)
            sizebot = font.getsize(bottext)
            top = round((rowsize-sizetop[1]-sizebot[1])/2)
            left = round((columnsize-sizetop[0])/2)
            draw.text((left,top),toptext,font=font)
            top += sizetop[1]
            left = round((columnsize-sizebot[0])/2)
            draw.text((left,top),bottext,font=font)
        else:
            rows = ['SOLO','DUO','SQUAD']
            text = 'Overall'
            size = font.getsize(text)
            left = round((columnsize-size[0])/2)
            top = round((rowsize-size[1])/2)
            draw.text((left,top),text,font=font)
        columns = ['KD','WINS','KILLS','WIN%','MATCHES','RATING']
        for i in range(1,4):
            row = rows[i-1]
            draw.rectangle([(4,rowsize*i+4),(columnsize-4,rowsize*(i+1)-4)],fill=DEFAULT_COLOR)
            if row.find('SOLO') > -1:
                text = 'solos'
            elif row.find('DUO') > -1:
                text = 'duos'
            elif row.find('SQUAD') > -1:
                text = 'squads'
            else:
                text = ''
            size = font.getsize(text)
            top = round((rowsize*i)+((rowsize-size[1])/2))
            left = round((columnsize-size[0])/2)
            draw.text((left,top),text,fill=fg,font=font)
        left = columnsize
        for column in columns:
            draw.rectangle([(left+4,4),(left+columnsize-4,rowsize-4)],fill=DEFAULT_COLOR)
            textsize = font.getsize(column)
            top = round((rowsize-textsize[1])/2)
            rleft = round(left + ((columnsize-textsize[0])/2))
            draw.text((rleft,top),column,fill=fg,font=font)
            c = column.lower()
            if c == 'win%':
                c = 'win_percent'
            top = rowsize
            for row in rows:
                stat = getattr(stats,row.lower(),None)
                draw.rectangle([(left+4,top+4),(left+columnsize-4,top+rowsize-4)],fill=DEFAULT_COLOR)
                if stat != None:
                    value = getattr(stat,c,'0')
                    if value.strip() == '':
                        value = '0'
                    if value is not None:
                        textsize = font.getsize(value)
                        rleft = round(left + ((columnsize-textsize[0])/2))
                        rtop = round(top+ ((rowsize-textsize[1])/2))
                        draw.text((rleft,rtop),value,fill=fg,font=font)
                    else:
                        LOGGER.warning('Column %s not found', c)
                top += rowsize
            left += columnsize
        return image
class ImageGenerator:
    def __init__(self):
        self.background = Background(color=(0,0,0,0))
        self.overlays = []
    def setBackground(self, color=None, url=None):
        if url != None:
            self.background.url = url
        if color != None:
            self.background.color = color
    def addOverlay(self, overlay):
        self.overlays.append(overlay)
    @asyncio.coroutine
    def generate(self, data):
        background = yield from self.background.generate()
        for overlay in self.overlays:
            overlay_image = yield from overlay.generate(data)
            background.paste(overlay_image,(0,0),overlay_image)
        return background
class StatsImage(ImageGenerator):
    def __init__(self):
        super().__init__()
        self.addOverlay(Overlay())
class PerformanceImage(ImageGenerator):
    def __init__(self):
        super().__init__()
        self.addOverlay(Performance(DEFAULT_SIZE))
class CurrentSeasonStatsImage(ImageGenerator):
    def __init__(self):
        super().__init__()
        self.addOverlay(Overlay(cs=True))

class StatsData:
    def __init__(self,data):
        if type(data) is dict:
            self.error = data.get('error',None)
            if self.error == None:
                self.userdata = UserData(data)
                self.lifetime = LifetimeStats(data.get('lifeTimeStats',[]))
                self.matches = Matches(data.get('recentMatches',[]))
                self.stats = Stats(data.get('stats',{}))
            # p2 solo p10 duo p9 squads
        else:
            raise RuntimeError('You must pass a dict argument')
class UserData:
    def __init__(self,data):
        self.account_id = data.get('accountId','')
        self.platform_id = data.get('platformId',0)
        self.platform = data.get('platformNameLong','')
        self.name = data.get('epicUserHandle','')
    def __iter__(self):
        yield 'account_id', self.account_id
        yield 'platform_id', self.platform_id
        yield 'platform', self.platform
        yield 'name', self.name
class LifetimeStats:
    def __init__(self,data):
        if type(data) is list:
            for item in data:
                key = item.get('key','')
                value = item.get('value','')
                if key == 'Top 3':
                    self.top_3 = value
                elif key == 'Top 5s':
                    self.top_5s = value
                elif key == 'Top 3s':
                    self.top_3s = value
                elif key == 'Top 6s':
                    self.top_6s = value
                elif key == 'Top 12s':
                    self.top_12s = value
                elif key == 'Top 25s':
                    self.top_25s = value
                elif key == 'Score':
                    self.score = value
                elif key == 'Matches Played':
                    self.matches = value
                elif key == 'Wins':
                    self.wins = value
                elif key == 'Kills':
                    self.kills = value
                elif key == 'K/d':
                    self.kd = value
        if getattr(self,'matches',None) != None and getattr(self,'wins',None) != None:
            self.win_percent = round((int(self.wins)/int(self.matches))*100,2)
    def __iter__(self):
        yield 'score', getattr(self,'score',None)
        yield 'matches', getattr(self,'matches',None)
        yield 'wins', getattr(self,'wins',None)
        yield 'kills', getattr(self,'kills',None)
        yield 'kd', getattr(self,'kd',None)
        yield 'win_percent', getattr(self,'win_percent',None)
class Matches(list):
    def __init__(self,data):
        if type(data) is list:
            for match in data:
                self.append(self.Match(match))
    class Match:
        def __init__(self,data):
            self.id = data.get('id',0)
            self.playlist = data.get('playlist','')
            self.kills = data.get('kills',0)
            self.matches = data.get('matches',0)
            self.score = data.get('score',0)
            self.platform = data.get('platform',0)
            self.time = data.get('dateCollected','')
            self.wins = data.get('top1',0)
            if self.matches != None and self.kills != None and self.wins != None:
                if self.matches == self.wins:
                    self.kd = self.kills
                else:
                    self.kd = self.kills/(self.matches-self.wins)
class Stats:
    def __init__(self,data):
        self.solo = self.Stat(data.get('p2',{}))
        self.duo = self.Stat(data.get('p10',{}))
        self.squad = self.Stat(data.get('p9',{}))
        self.curr_solo = self.Stat(data.get('curr_p2',{}))
        self.curr_duo = self.Stat(data.get('curr_p10',{}))
        self.curr_squad = self.Stat(data.get('curr_p9',{}))
        self.prev_solo = self.Stat(data.get('prior_p2',{}))
        self.prev_duo = self.Stat(data.get('prior_p10',{}))
        self.prev_squad = self.Stat(data.get('prior_p9',{}))
    class Stat:
        def __init__(self,data):
            self.score = self.getStat(data,'score')
            self.kd = self.getStat(data,'kd')
            self.win_percent = self.getStat(data,'winRatio')
            self.matches = self.getStat(data,'matches')
            self.kills = self.getStat(data,'kills')
            self.kills_per_game = self.getStat(data,'kpg')
            self.score_per_match = self.getStat(data,'scorePerMatch')
            self.wins = self.getStat(data,'top1')
            self.rating = self.getStat(data,'trnRating')
        @staticmethod
        def getStat(data,key):
            d = data.get(key,None)
            if d != None:
                o = d.get('value','')
            else:
                o = ''
            return o

class Map(dict):
    def __init__(self,ob,format_dec=False):
        if format_dec:
            for key, value in ob:
                self[key] = strings.strDec(value)
        else:
            super().__init__(ob)
    def __missing__(self, key):
        return key

class MatchEssential:
    def __init__(self,matchno,kd):
        self.match = matchno
        self.kd = kd

@asyncio.coroutine
def generate(KEY_TN,player,platform,backgrounds=[]):
    LOGGER.debug('backgrounds: %s', str(backgrounds))
    stats_data = yield from stats.stats(KEY_TN,player,platform)
    if stats_data['status'] == 200:
        stat_data = StatsData(stats_data)
        if stat_data.error == None:
            statsimage = StatsImage()
            if len(backgrounds) > 0:
                url = random.choice(backgrounds)
                LOGGER.debug('Chosen background: %s', url)
                statsimage.setBackground(url=url)
            image = yield from statsimage.generate(stat_data)
        else:
            image = None
    else:
        image = None
    return image

@asyncio.coroutine
def generate_season(KEY_TN, player, platform, backgrounds=[]):
    LOGGER.debug('backgrounds: %s', str(backgrounds))
    stats_data = yield from stats.stats(KEY_TN,player,platform)
    if stats_data['status'] == 200:
        stat_data = StatsData(stats_data)
        if stat_data.error == None:
            statsimage = CurrentSeasonStatsImage()
            if len(backgrounds) > 0:
                url = random.choice(backgrounds)
                LOGGER.debug('Chosen background: %s', url)
                statsimage.setBackground(url=url)
            image = yield from statsimage.generate(stat_data)
        else:
            image = None
    else:
        image = None
    return image

@asyncio.coroutine
def generate_performance(KEY_TN, player, platform, backgrounds=[]):
    LOGGER.debug('backgrounds: %s', str(backgrounds))
    stats_data = yield from stats.stats(KEY_TN,player,platform)
    if stats_data['status'] == 200:
        stat_data = StatsData(stats_data)
        if stat_data.error == None:
            statsimage = PerformanceImage()
            if len(backgrounds) > 0:
                url = random.choice(backgrounds)
                LOGGER.debug('Chosen background: %s', url)
                statsimage.setBackground(url=url)
            image = yield from statsimage.generate(stat_data)
        else:
            image = None
    else:
        image = None
    return image
