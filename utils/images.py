import math
import asyncio
import aiohttp
from io import BytesIO
import PIL.Image

@asyncio.coroutine
def radial_gradient(draw,width,height,color_inner,color_outer): # will overite everything in image
    """Creates a radial gradient on an image. Might be slow"""
    alpha = False
    if len(color_inner) == 4 and len(color_outer) == 4:
        alpha = True
    for x in range(width):
        for y in range(height):
            dToE = math.sqrt((x -width/2) ** 2 + (y - height/2) ** 2)
            dToE = float(dToE) / (math.sqrt(2) * width/2)
            r = round(color_inner[0] * dToE + color_outer[0] * (1-dToE))
            g = round(color_inner[1] * dToE + color_outer[1] * (1-dToE))
            b = round(color_inner[2] * dToE + color_outer[2] * (1-dToE))
            if alpha:
                a = round(color_inner[3] * dToE + color_outer[3] * (1-dToE))
                color = (r,g,b,a)
            else:
                color = (r,g,b)
            draw.point((x,y),fill=color)
def darken(color,alpha):
    """Darkens a color to specified alpha"""
    return (color[0],color[1],color[2],alpha)
class Background:
    def __init__(self,size,color=None,url=None):
        if (color == None and url == None) or (color != None and url != None):
            raise RuntimeError('You must specify either color or url not both or neither.')
        if color != None:
            self.color = color
        elif url != None:
            self.url = url
        self.size = size
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
