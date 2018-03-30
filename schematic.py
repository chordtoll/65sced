fn='6502.sch'


import pygame
import math
import sys
import os

import decodePLA

from atomicwrites import atomic_write

from layerdict import LayerDict

WIDTH=800
HEIGHT=720

grid=True
rendering=False

pygame.init()
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Schematic")
pygame.key.set_repeat(500,50)

running=True
clock = pygame.time.Clock()

pygame.font.init()


zoom=0
tw=[32,64,128,256][zoom]
gw=tw/2
sw=gw/8
fs=sw*6
lw=sw/2

font=pygame.font.SysFont("lucidaconsole",fs)

def text1(word,x,y):
  font = pygame.font.SysFont(None, 25)
  text = font.render("{}".format(word), True, RED)
  return screen.blit(text,(x,y))

U=0
D=2
L=3
R=1


class State():
  def __init__(self,value=0,strength=0):
    self.value=value
    self.strength=strength
  def __add__(a,b):
    if a.strength==b.strength:
      if a.value==b.value:
        return State(a.value,a.strength)
      return State(0,a.strength)
    if a.strength>b.strength:
      return State(a.value,a.strength)
    return State(b.value,b.strength)
  def __repr__(self):
    return [['vl','vh'],['l ','h '],['L ','H '],['V-','V+']][self.strength][self.value]
  def __eq__(a,b):
    return repr(a)==repr(b)
  def __ne__(a,b):
    return not a.__eq__(b)
  def __hash__(self):
    return hash(repr(self))

sts=[]
print '   |',
for stren in [0,1,2,3]:
  for val in [0,1]:
    sts.append(State(val,stren))
    print State(val,stren),
print
print "---+------------------------"

for a in sts:
  print a,'|',
  for b in sts:
    print a+b,
  print


print "Checking commutative:",
for a in sts:
  for b in sts:
    assert a+b==b+a
print "OK"
print "Checking associative:",
for a in sts:
  for b in sts:
    for c in sts:
      assert (a+b)+c==a+(b+c)
print "OK"

tiles=LayerDict()
#tiles.addlayer("DDriver7",3,2,30,16)
#tiles.addlayer("DDriver6",3,16,30,30)
wires=set()
nodes={}
nodepoints={}

class Node():
  def __init__(self,n):
    self.n=n
    self.state=State()

def node(n):
  if n==-1:
    return Node()
  if n not in nodes:
    nodes[n]=Node(n)
  return nodes[n]

node(558).state=State(0,3)
node(657).state=State(1,3)

class Pin():
  def __init__(self,n=-1,d=U,name=""):
    self.d=int(d)
    self.n=int(n)
    self.name=name
  def dump(self):
    return 'P:%d,%d,%s'%(self.n,self.d,self.name)
  def nodepoints(self):
    dd=[(1,0),(2,1),(1,2),(0,1)]
    return [(dd[self.d],self.n)]
  def place(self,x,y):
    dd=[(1,0),(2,1),(1,2),(0,1)]
    if (dd[self.d][0]+x,dd[self.d][1]+y) in nodepoints:
      if nodepoints[(dd[self.d][0]+x,dd[self.d][1]+y)]!=-1:
        self.n=nodepoints[dd[self.d][0]+x,dd[self.d][1]+y]
  def draw(self,screen,x,y):
    color=(255,255,255)
    if self.n!=-1:
      color=[192-(node(self.n).state.strength*64)]*3
      if node(self.n).state.value==0:
        color[0]=255
      else:
        color[1]=255
    else:
      color=(255,0,255)
    if self.d==U:
      pygame.draw.circle(screen,color,(x+sw*8,y+sw*8),sw*2)
      pygame.draw.line(screen,color,(x+sw*8,y+sw*8),(x+sw*8,y),lw)
    if self.d==D:
      pygame.draw.circle(screen,color,(x+sw*8,y+sw*8),sw*2)
      pygame.draw.line(screen,color,(x+sw*8,y+sw*8),(x+sw*8,y+tw),lw)
    if self.d==R:
      pygame.draw.circle(screen,color,(x+sw*8,y+sw*8),sw*2)
      pygame.draw.line(screen,color,(x+sw*8,y+sw*8),(x+tw,y+sw*8),lw)
    if self.d==L:
      pygame.draw.circle(screen,color,(x+sw*8,y+sw*8),sw*2)
      pygame.draw.line(screen,color,(x+sw*8,y+sw*8),(x,y+sw*8),lw)
    text=font.render(self.name,False,(255,255,255))
    if self.d in [D,R]:
      screen.blit(text,(x,y))
    else:
      screen.blit(text,(x,y+tw-text.get_height()))

class Label():
  def __init__(self,n=-1,d=U):
    self.d=int(d)
    self.n=int(n)
  def dump(self):
    return 'L:%d,%d'%(self.n,self.d)
  def nodepoints(self):
    dd=[(1,0),(2,1),(1,2),(0,1)]
    return [(dd[self.d],self.n)]
  def place(self,x,y):
    dd=[(1,0),(2,1),(1,2),(0,1)]
    if (dd[self.d][0]+x,dd[self.d][1]+y) in nodepoints:
      if nodepoints[(dd[self.d][0]+x,dd[self.d][1]+y)]!=-1:
        self.n=nodepoints[dd[self.d][0]+x,dd[self.d][1]+y]
  def draw(self,screen,x,y):
    color=(255,255,255)
    if self.n!=-1:
      color=[192-(node(self.n).state.strength*64)]*3
      if node(self.n).state.value==0:
        color[0]=255
      else:
        color[1]=255
    else:
      color=(255,0,255)
    if self.d==U:
      pygame.draw.line(screen,color,(x+sw*8,y),(x+sw*10,y+sw*2),lw)
      pygame.draw.line(screen,color,(x+sw*8,y),(x+sw*6,y+sw*2),lw)
    if self.d==D:
      pygame.draw.line(screen,color,(x+sw*8,y+tw),(x+sw*10,y+sw*14),lw)
      pygame.draw.line(screen,color,(x+sw*8,y+tw),(x+sw*6,y+sw*14),lw)
    if self.d==R:
      pygame.draw.line(screen,color,(x+tw,y+sw*8),(x+sw*14,y+sw*10),lw)
      pygame.draw.line(screen,color,(x+tw,y+sw*8),(x+sw*14,y+sw*6),lw)
    if self.d==L:
      pygame.draw.line(screen,color,(x,y+sw*8),(x+sw*2,y+sw*10),lw)
      pygame.draw.line(screen,color,(x,y+sw*8),(x+sw*2,y+sw*6),lw)
    if self.n!=-1:
      text=font.render(decodePLA.nodename1(self.n),False,(255,255,255))
      if self.d==U:
        screen.blit(text,(x+(tw-text.get_width())/2,y+sw*2))
      elif self.d==D:
        screen.blit(text,(x+(tw-text.get_width())/2,y+sw*8))
      elif self.d==L:
        screen.blit(text,(x+sw*3,y+(tw-text.get_height())/2))
      elif self.d==R:
        screen.blit(text,(x+sw*13-text.get_width(),y+(tw-text.get_height())/2))

class Pullup():
  def __init__(self,n=-1,d=U):
    self.d=int(d)
    self.n=int(n)
  def dump(self):
    return 'U:%d,%d'%(self.n,self.d)
  def nodepoints(self):
    dd=[(1,0),(2,1),(1,2),(0,1)]
    return [(dd[self.d],self.n)]
  def place(self,x,y):
    dd=[(1,0),(2,1),(1,2),(0,1)]
    if (dd[self.d][0]+x,dd[self.d][1]+y) in nodepoints:
      self.n=nodepoints[dd[self.d][0]+x,dd[self.d][1]+y]
  def draw(self,screen,x,y):
    color=(255,255,255)
    if self.n!=-1:
      color=[192-(node(self.n).state.strength*64)]*3
      if node(self.n).state.value==0:
        color[0]=255
      else:
        color[1]=255
    else:
      color=(255,0,255)
    if self.d==U:
      pygame.draw.line(screen,color,(x+sw*8,y+sw*8),(x+sw*8,y),lw)
      pygame.draw.polygon(screen,(0,255,0),[(x+sw*6,y+sw*6),(x+sw*10,y+sw*6),(x+sw*8,y+sw*10)])
    if self.d==D:
      pygame.draw.line(screen,color,(x+sw*8,y+sw*8),(x+sw*8,y+tw),lw)
      pygame.draw.polygon(screen,(0,255,0),[(x+sw*6,y+sw*10),(x+sw*10,y+sw*10),(x+sw*8,y+sw*6)])      
    if self.d==R:
      pygame.draw.line(screen,color,(x+sw*8,y+sw*8),(x+tw,y+sw*8),lw)
      pygame.draw.polygon(screen,(0,255,0),[(x+sw*10,y+sw*6),(x+sw*10,y+sw*10),(x+sw*6,y+sw*8)])
    if self.d==L:
      pygame.draw.line(screen,color,(x+sw*8,y+sw*8),(x,y+sw*8),lw)
      pygame.draw.polygon(screen,(0,255,0),[(x+sw*6,y+sw*6),(x+sw*6,y+sw*10),(x+sw*10,y+sw*8)])

class Wire():
  def __init__(self,n,np1,np2):
    self.n=n
    self.x1,self.y1=np1
    self.x2,self.y2=np2
  def dump(self):
    x1,y1,g1=tiles.xy2xyg(self.x1,self.y1)
    x2,y2,g2=tiles.xy2xyg(self.x2,self.y2)
    return '%d,%d,%d:%d,%d,%d:%d'%(x1,y1,g1,x2,y2,g2,self.n)
  def span(self):
    x,y,g1=tiles.xy2xyg(self.x1,self.y1)
    x,y,g2=tiles.xy2xyg(self.x2,self.y2)
    return None if g1!=g2 else g1
  def nodepoints(self):
    return [((self.x1,self.y1),self.n),((self.x2,self.y2),self.n)]
  def draw(self,screen,tl):
    if self.n!=-1:
      color=[192-(node(self.n).state.strength*64)]*3
      if node(self.n).state.value==0:
        color[0]=255
      else:
        color[1]=255
    else:
      color=(255,0,255)
    pygame.draw.circle(screen,color,((self.x1-tl[0])*gw,(self.y1-tl[1])*gw),lw*2)
    pygame.draw.circle(screen,color,((self.x2-tl[0])*gw,(self.y2-tl[1])*gw),lw*2)
    pygame.draw.line(screen,color,((self.x1-tl[0])*gw,(self.y1-tl[1])*gw),((self.x2-tl[0])*gw,(self.y2-tl[1])*gw),lw)

class Transistor():
  def __init__(self,n=-1,d=U,a=-1,b=-1,c=-1):
    self.d=int(d)
    self.n=int(n)
    self.nodes=[int(a),int(b),int(c)]
  def isOn(self):
    return self.nodes[1].state.value==1
  def dump(self):
    return 'T:%d,%d,%d,%d,%d'%(self.n,self.d,self.nodes[0],self.nodes[1],self.nodes[2])
  def nodepoints(self):
    npd=[[1,2,-1,0],
         [0,1,2,-1],
         [-1,0,1,2],
         [2,-1,0,1]]
    dd=[(1,0),(2,1),(1,2),(0,1)]
    npar=[]
    for dr in [U,R,D,L]:
      np=npd[self.d][dr]
      if np!=-1:
        npar.append((dd[dr],self.nodes[np]))
    return npar
  def place(self,x,y):
    npd=[[1,2,-1,0],
         [0,1,2,-1],
         [-1,0,1,2],
         [2,-1,0,1]]
    dd=[(1,0),(2,1),(1,2),(0,1)]
    for dr in [U,R,D,L]:
      np=npd[self.d][dr]
      if np!=-1 and (dd[dr][0]+x,dd[dr][1]+y) in nodepoints:
        self.nodes[np]=nodepoints[dd[dr][0]+x,dd[dr][1]+y]
  def draw(self,screen,x,y):
    colors=[(255,255,255),(255,255,255),(255,255,255)]
    for j,i in enumerate(self.nodes):
      if i!=-1:
        colors[j]=[192-(node(i).state.strength*64)]*3
        if node(i).state.value==0:
          colors[j][0]=255
        else:
          colors[j][1]=255
      else:
        colors[j]=(255,0,255)
    if self.d in [U,D]:
      pygame.draw.line(screen,colors[0 if self.d==U else 2],(x,y+sw*8),(x+sw*6,y+sw*8),lw)
      pygame.draw.line(screen,colors[2 if self.d==U else 0],(x+sw*10,y+sw*8),(x+tw,y+sw*8),lw)
    else:
      pygame.draw.line(screen,colors[0 if self.d==R else 2],(x+sw*8,y),(x+sw*8,y+sw*6),lw)
      pygame.draw.line(screen,colors[2 if self.d==R else 0],(x+sw*8,y+sw*10),(x+sw*8,y+tw),lw)
    if self.d==U:
      if self.nodes[0]!=-1:
        if node(self.nodes[0]).state.value==0 and node(self.nodes[0]).state.strength==3:
          pygame.draw.line(screen,(255,0,0),(x,y+sw*9),(x,y+sw*7),lw)
        if node(self.nodes[0]).state.value==1 and node(self.nodes[0]).state.strength==3:
          pygame.draw.circle(screen,(0,255,0),(x,y+sw*8),lw*3)
      if self.nodes[2]!=-1:
        if node(self.nodes[2]).state.value==0 and node(self.nodes[2]).state.strength==3:
          pygame.draw.line(screen,(255,0,0),(x+tw,y+sw*9),(x+tw,y+sw*7),lw)
        if node(self.nodes[2]).state.value==1 and node(self.nodes[2]).state.strength==3:
          pygame.draw.circle(screen,(0,255,0),(x+tw,y+sw*8),lw*3)
      pygame.draw.line(screen,(255,255,255),(x+sw*6,y+sw*8),(x+sw*6,y+sw*4),lw)      #
      pygame.draw.line(screen,(255,255,255),(x+sw*6,y+sw*4),(x+sw*10,y+sw*4),lw)     # Arch
      pygame.draw.line(screen,(255,255,255),(x+sw*10,y+sw*4),(x+sw*10,y+sw*8),lw)    #

      pygame.draw.line(screen,colors[1],(x+sw*8,y),(x+sw*8,y+sw*2),lw)           # Gate
      pygame.draw.line(screen,colors[1],(x+sw*6,y+sw*2),(x+sw*10,y+sw*2),lw)     #
    if self.d==D:
      if self.nodes[2]!=-1:
        if node(self.nodes[2]).state.value==0 and node(self.nodes[2]).state.strength==3:
          pygame.draw.line(screen,(255,0,0),(x,y+sw*9),(x,y+sw*7),lw)
        if node(self.nodes[2]).state.value==1 and node(self.nodes[2]).state.strength==3:
          pygame.draw.circle(screen,(0,255,0),(x,y+sw*8),lw*3)
      if self.nodes[0]!=-1:
        if node(self.nodes[0]).state.value==0 and node(self.nodes[0]).state.strength==3:
          pygame.draw.line(screen,(255,0,0),(x+tw,y+sw*9),(x+tw,y+sw*7),lw)
        if node(self.nodes[0]).state.value==1 and node(self.nodes[0]).state.strength==3:
          pygame.draw.circle(screen,(0,255,0),(x+tw,y+sw*8),lw*3)
      pygame.draw.line(screen,(255,255,255),(x+sw*6,y+sw*8),(x+sw*6,y+sw*12),lw)     #
      pygame.draw.line(screen,(255,255,255),(x+sw*6,y+sw*12),(x+sw*10,y+sw*12),lw)   # Arch
      pygame.draw.line(screen,(255,255,255),(x+sw*10,y+sw*12),(x+sw*10,y+sw*8),lw)   #

      pygame.draw.line(screen,colors[1],(x+sw*8,y+tw),(x+sw*8,y+sw*14),lw)       # Gate
      pygame.draw.line(screen,colors[1],(x+sw*6,y+sw*14),(x+sw*10,y+sw*14),lw)   #
    if self.d==R:
      if self.nodes[0]!=-1:
        if node(self.nodes[0]).state.value==0 and node(self.nodes[0]).state.strength==3:
          pygame.draw.line(screen,(255,0,0),(x+sw*9,y),(x+sw*7,y),lw)
        if node(self.nodes[0]).state.value==1 and node(self.nodes[0]).state.strength==3:
          pygame.draw.circle(screen,(0,255,0),(x+sw*8,y),lw*3)
      if self.nodes[2]!=-1:
        if node(self.nodes[2]).state.value==0 and node(self.nodes[2]).state.strength==3:
          pygame.draw.line(screen,(255,0,0),(x+sw*9,y+tw),(x+sw*7,y+tw),lw)
        if node(self.nodes[2]).state.value==1 and node(self.nodes[2]).state.strength==3:
          pygame.draw.circle(screen,(0,255,0),(x+sw*8,y+tw),lw*3)
      pygame.draw.line(screen,(255,255,255),(x+sw*8,y+sw*6),(x+sw*12,y+sw*6),lw)     #
      pygame.draw.line(screen,(255,255,255),(x+sw*12,y+sw*6),(x+sw*12,y+sw*10),lw)   # Arch
      pygame.draw.line(screen,(255,255,255),(x+sw*12,y+sw*10),(x+sw*8,y+sw*10),lw)   #

      pygame.draw.line(screen,colors[1],(x+tw,y+sw*8),(x+sw*14,y+sw*8),lw)       # Gate
      pygame.draw.line(screen,colors[1],(x+sw*14,y+sw*6),(x+sw*14,y+sw*10),lw)   #
    if self.d==L:
      if self.nodes[2]!=-1:
        if node(self.nodes[2]).state.value==0 and node(self.nodes[2]).state.strength==3:
          pygame.draw.line(screen,(255,0,0),(x+sw*9,y),(x+sw*7,y),lw)
        if node(self.nodes[2]).state.value==1 and node(self.nodes[2]).state.strength==3:
          pygame.draw.circle(screen,(0,255,0),(x+sw*8,y),lw*3)
      if self.nodes[0]!=-1:
        if node(self.nodes[0]).state.value==0 and node(self.nodes[0]).state.strength==3:
          pygame.draw.line(screen,(255,0,0),(x+sw*9,y+tw),(x+sw*7,y+tw),lw)
        if node(self.nodes[0]).state.value==1 and node(self.nodes[0]).state.strength==3:
          pygame.draw.circle(screen,(0,255,0),(x+sw*8,y+tw),lw*3)
      pygame.draw.line(screen,(255,255,255),(x+sw*8,y+sw*6),(x+sw*4,y+sw*6),lw)      #
      pygame.draw.line(screen,(255,255,255),(x+sw*4,y+sw*6),(x+sw*4,y+sw*10),lw)     # Arch
      pygame.draw.line(screen,(255,255,255),(x+sw*4,y+sw*10),(x+sw*8,y+sw*10),lw)    #

      pygame.draw.line(screen,colors[1],(x,y+sw*8),(x+sw*2,y+sw*8),lw)           # Gate
      pygame.draw.line(screen,colors[1],(x+sw*2,y+sw*6),(x+sw*2,y+sw*10),lw)     #

def popsnp(x,y,v):
  npk=(x,y)
  if npk in nodepoints:
    if nodepoints[npk]==-1:
      nodepoints[npk]=v
      for i in tiles:
        if abs(i[0]-npk[0])<3 and abs(i[1]-npk[1])<3:
          tiles[i].place(i[0],i[1])
    else:
      assert nodepoints[npk]==v
  else:
    nodepoints[npk]=v

def popnp(x,y,obj):
  for k,v in obj.nodepoints():
    npk=(x+k[0],y+k[1])
    if npk in nodepoints:
      if nodepoints[npk]==-1:
        nodepoints[npk]=v
        for i in tiles:
          if abs(i[0]-npk[0])<3 and abs(i[1]-npk[1])<3:
            tiles[i].place(i[0],i[1])
      else:
        assert nodepoints[npk]==v
    else:
      nodepoints[npk]=v

def save():
  #return
  print "Saving:",
  for i in tiles.layers:
    if i.dirty:
      print i.id,
      with atomic_write(os.path.join('layers','%s.sch'%i.name), overwrite=True) as f:
        f.write('#%s,%d,%d,%d,%d,%d            %%name:%s, @(%d,%d) %dx%d #%d\n'%(i.name,i.x1,i.y1,i.x2-i.x1,i.y2-i.y1,i.id,i.name,i.x1,i.y1,i.x2-i.x1,i.y2-i.y1,i.id))
        for t in sorted(i.dict.keys()):
          f.write('T%i,%i:%s\n'%(t[0],t[1],i.dict[t].dump()))
        for w in sorted(list(wires),key=lambda x:x.dump()):
          if w.span()==i.id:
            f.write('W%s\n'%(w.dump()))  
      i.dirty=False
  print "wires"
  with atomic_write('wires.sch', overwrite=True) as f:
    for i in sorted(list(wires),key=lambda x:x.dump()):
      if i.span() is None:
        f.write('W%s\n'%(i.dump()))
  #with open(fn,'w') as f:
    #for i in tiles:
    #  f.write('T%i,%i:%s\n'%(i[0],i[1],tiles[i].dump()))
  #  for i in wires:
  #    f.write('W%s\n'%(i.dump()))
def load():
  for fn in os.listdir('layers'):
    with open(os.path.join('layers',fn),'r') as f:
      for line in f:
        line=line.rstrip()
        line=line.split('%')[0]
        if line[0]=='#':
          name,x1,y1,w,h,lid=line[1:].split(',')
          x1=int(x1)
          x2=x1+int(w)
          y1=int(y1)
          y2=y1+int(h)
          lid=int(lid)
          tiles.addlayer(name,x1,y1,x2,y2,lid)
        if line[0]=='T':
          desig,cat,param=line[1:].split(':')
          print desig,cat,param
          desig=[int(i) for i in desig.split(',')]
          param=param.split(',')
          obj=None
          if cat=='T':
            obj=Transistor(*param)
          if cat=='P':
            obj=Pin(*param)
          if cat=='U':
            obj=Pullup(*param)
          if cat=='L':
            obj=Label(*param)
          desig[0]+=int(x1)
          desig[1]+=int(y1)
          tiles[(int(desig[0]),int(desig[1]))]=obj
          popnp(int(desig[0]),int(desig[1]),obj)
        if line[0]=='W':
          w1,w2,n=line[1:].split(':')
          print w1,w2,n
          w1=[int(i) for i in w1.split(',')]
          w2=[int(i) for i in w2.split(',')]
          w1=tiles.xyg2xy(*w1)
          w2=tiles.xyg2xy(*w2)
          n=int(n)
          w=Wire(n,w1,w2)
          wires.add(w)
          popnp(0,0,w)
  with open('wires.sch','r') as f:
    for line in f:
      if line.rstrip()=='':
        continue
      assert line[0]=='W'
      w1,w2,n=line[1:].split(':')
      print w1,w2,n
      w1=[int(i) for i in w1.split(',')]
      w2=[int(i) for i in w2.split(',')]
      w1=tiles.xyg2xy(*w1)
      w2=tiles.xyg2xy(*w2)
      n=int(n)
      w=Wire(n,w1,w2)
      wires.add(w)
      popnp(0,0,w)



load()

tl=(0,0)


active=None
crsq=None
crnd=None
plsq=None
w1sq=None
w2sq=None
rot=0
instr=""

def occupied(sq):
  for x in [sq[0],sq[0]]:
    for y in [sq[1],sq[1]]:
      if (x,y) in tiles:
        return True
  return False

def translate(x,y,tuple):
  return (x+tuple[0],y+tuple[1])

def render():
  if grid and not rendering:
    for x in xrange(WIDTH/gw):
      for y in xrange(HEIGHT/gw):
        pygame.draw.rect(screen,(50,50,50),(x*gw,y*gw,gw,gw),1)
  for i in tiles.rects():
    x1,y1=translate(-tl[0],-tl[1],i[0])
    x2,y2=translate(-tl[0],-tl[1],i[1])
    text=font.render(i[2].name,False,(255,255,0))
    screen.blit(text,(x1*gw+2,y1*gw+1))
    pygame.draw.rect(screen,(0,0,128),(x1*gw,y1*gw,(x2-x1)*gw,(y2-y1)*gw),1)
  if mode in [MODE_addtx,MODE_txid]:
    if plsq:
      x,y=translate(plsq[0],plsq[1],[-i for i in tl])
      if occupied(plsq):
        pygame.draw.rect(screen,(255,0,0),(x*gw,y*gw,tw,tw),1)
      else:
        pygame.draw.rect(screen,(0,0,255),(x*gw,y*gw,tw,tw),1)
      Transistor(d=rot).draw(screen,x*gw,y*gw)
  if mode in [MODE_addpn,MODE_pnid]:
    if plsq:
      x,y=translate(plsq[0],plsq[1],[-i for i in tl])
      if occupied(plsq):
        pygame.draw.rect(screen,(255,0,0),(x*gw,y*gw,tw,tw),1)
      else:
        pygame.draw.rect(screen,(0,0,255),(x*gw,y*gw,tw,tw),1)
      Pin(d=rot).draw(screen,x*gw,y*gw)
  if mode in [MODE_addlb,MODE_lbid]:
    if plsq:
      x,y=translate(plsq[0],plsq[1],[-i for i in tl])
      if occupied(plsq):
        pygame.draw.rect(screen,(255,0,0),(x*gw,y*gw,tw,tw),1)
      else:
        pygame.draw.rect(screen,(0,0,255),(x*gw,y*gw,tw,tw),1)
      Label(d=rot).draw(screen,x*gw,y*gw)
  if mode in [MODE_addpu]:
    if plsq:
      x,y=translate(plsq[0],plsq[1],[-i for i in tl])
      if occupied(plsq):
        pygame.draw.rect(screen,(255,0,0),(x*gw,y*gw,tw,tw),1)
      else:
        pygame.draw.rect(screen,(0,0,255),(x*gw,y*gw,tw,tw),1)
      Pullup(d=rot).draw(screen,x*gw,y*gw)
  for x in xrange(WIDTH/gw):
    for y in xrange(HEIGHT/gw):
      if translate(x,y,tl) in tiles:
        tiles[translate(x,y,tl)].draw(screen,x*gw,y*gw)
  for i in wires:
    i.draw(screen,tl)
  if not rendering:
    pygame.draw.rect(screen,(0,0,0),(0,0,WIDTH,2*gw),0)
    if crsq:
      for x,y in [(0,0),(0,-1),(-1,0),(-1,-1)]:
        cr=translate(x,y,crsq)
        if cr in tiles:
          if tiles[cr].dump()[0]=='T':
            text=font.render('T%i'%tiles[cr].n,False,(255,255,255))
            screen.blit(text,(3*tw,0))
    if crnd:
      if crnd in nodepoints:
        text=font.render('N%i (%s)'%(nodepoints[crnd],decodePLA.nodename1(nodepoints[crnd])),False,(255,255,255))
        screen.blit(text,(3*tw,gw))
  if mode in [MODE_wire1,MODE_wire2]:
    if w1sq:
      x,y=translate(w1sq[0],w1sq[1],[-i for i in tl])
      pygame.draw.circle(screen,(0,0,255),(x*gw,y*gw),lw*2)
    if mode==MODE_wire2:
      if w2sq:
        x2,y2=translate(w2sq[0],w2sq[1],[-i for i in tl])
        pygame.draw.circle(screen,(0,0,255),(x2*gw,y2*gw),lw*2)
        pygame.draw.line(screen,(255,255,255),(x*gw,y*gw),(x2*gw,y2*gw),lw)
  #for k in nodepoints:
  #  x,y=translate(k[0],k[1],[-i for i in tl])
  #  pygame.draw.circle(screen,(0,0,255),(x*gw,y*gw),2)
  if not rendering:
    text=font.render(str(crsq),False,(255,255,255))
    screen.blit(text,(0,0))
  if mode in inmodes:
    text=font.render(">"+instr,False,(255,255,255))
    screen.blit(text,(0,gw))

def input_complete(inp,mode):
  global plsq
  global w1sq
  global w2sq
  if mode==MODE_txid:
    tiles[plsq]=Transistor(int(inp),rot)
  if mode==MODE_pnid:
    tiles[plsq]=Pin(name=inp,d=rot)
  if mode==MODE_lbid:
    try:
      nid=int(inp)
    except:
      nid=decodePLA.findnode(inp)
    tiles[plsq]=Label(n=nid,d=rot)
  if mode==MODE_wnid:
    try:
      nid=int(inp)
    except:
      nid=decodePLA.findnode(inp)
    if w1sq==w2sq:
      popsnp(w1sq[0],w1sq[1],nid)
      tiles.layerat(w1sq[0],w1sq[1]).dirty=True
    else:
      w=Wire(nid,w1sq,w2sq)
      wires.add(w)
      popnp(0,0,w)
      span=w.span()
      print "Span",span
      if span is None:
        for i in tiles.layers:
          i.dirty=True
      else:
        tiles.layerid(span).dirty=True
    #save()
    w1sq=None
    w2sq=None
    return
  tiles[plsq].place(plsq[0],plsq[1])
  popnp(plsq[0],plsq[1],tiles[plsq])
  save()
  plsq=None

if '-n' in sys.argv:
  grid=False

MODE_idle=0
MODE_addtx=1
MODE_txid=2
MODE_addpn=3
MODE_pnid=4
MODE_wire1=5
MODE_wire2=6
MODE_wnid=7
MODE_addpu=8
MODE_pwr=10
MODE_gnd=11
MODE_addlb=12
MODE_lbid=13

mode=MODE_idle
inmodes=[MODE_txid,MODE_pnid,MODE_wnid,MODE_lbid]

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == pygame.KEYDOWN:
      if event.key==pygame.K_ESCAPE:
        mode=MODE_idle
      if mode in inmodes:
        if event.key==pygame.K_BACKSPACE:
          instr=instr[:-1]
        elif event.unicode in ['\r','\n','\r\n']:
          input_complete(instr,mode)
          instr=""
          mode=MODE_idle
        else:
          instr+=event.unicode
      else:
        if event.key==pygame.K_UP:
          tl=(tl[0],tl[1]-3)
        if event.key==pygame.K_LEFT:
          tl=(tl[0]-3,tl[1])
        if event.key==pygame.K_DOWN:
          tl=(tl[0],tl[1]+3)
        if event.key==pygame.K_RIGHT:
          tl=(tl[0]+3,tl[1])
        if event.unicode=='s':
          for i in tiles.layers:
            i.dirty=True
          save() 
        if event.unicode=='t':
          mode=MODE_addtx
        if event.unicode=='p':
          mode=MODE_addpn
        if event.unicode=='u':
          mode=MODE_addpu
        if event.unicode=='r':
          rot=(rot+1)%4
        if event.unicode=='w':
          mode=MODE_wire1
        if event.unicode=='l':
          mode=MODE_addlb
        if event.unicode=='1':
          popsnp(crnd[0],crnd[1],657)
          save()
        if event.unicode=='0':
          popsnp(crnd[0],crnd[1],558)
          save()
        if event.unicode=='x':
          nx,xx,ny,xy=tiles.albb()
          otl=tl
          rendering=True
          tx=[]
          ty=[]
          for x in xrange(0,xx,(WIDTH/gw)):
            for y in xrange(0,xy,(HEIGHT/gw)):
              tl=(x,y)
              screen.fill((0,0,0))
              render()
              pygame.display.flip()
              clock.tick(60)
              pygame.image.save(screen, "tiles/tile.%04d.%04d.png"%(x,y))
            os.system('c:\\cygwin64\\bin\\convert tiles/tile.%04d.*.png -append tiles/tile.%04d.all.png"'%(x,x))
          os.system('c:\\cygwin64\\bin\\convert tiles/tile.*.all.png +append schematic.png"')
          os.system('rm tiles/tile*')
          tl=otl
          rendering=False
    if event.type == pygame.MOUSEBUTTONDOWN:
      #active=translate((event.pos[0]/tw),(event.pos[1]/tw),tl)
      if mode==MODE_addtx:
        if plsq and not occupied(plsq):
          mode=MODE_txid
      if mode==MODE_addpn:
        if plsq and not occupied(plsq):
          mode=MODE_pnid
      if mode==MODE_addlb:
        if plsq and not occupied(plsq):
          if translate(plsq[0],plsq[1],Label(d=rot).nodepoints()[0][0]) in nodepoints and nodepoints[translate(plsq[0],plsq[1],Label(d=rot).nodepoints()[0][0])]!=-1:
            mode=MODE_lbid
            input_complete('-1',MODE_lbid)
            mode=MODE_idle
          else:
            mode=MODE_lbid
      if mode==MODE_addpu:
        if plsq and not occupied(plsq):
          tiles[plsq]=Pullup(d=rot)
          tiles[plsq].place(plsq[0],plsq[1])
          popnp(plsq[0],plsq[1],tiles[plsq])
          save()
          plsq=None
          mode=MODE_idle
      if mode==MODE_wire1:
        if w1sq:
          mode=MODE_wire2
        continue
      if mode==MODE_wire2:
        wnod=-1
        if w2sq:
          if w1sq in nodepoints and nodepoints[w1sq]!=-1 and w2sq in nodepoints and nodepoints [w2sq]!=-1:
            assert nodepoints[w1sq]==nodepoints[w2sq]
          if w1sq in nodepoints and nodepoints[w1sq]!=-1:
            wnod=nodepoints[w1sq]
          elif w2sq in nodepoints and nodepoints[w2sq]!=-1:
            wnod=nodepoints[w2sq]
          else:
            mode=MODE_wnid
            continue
        if w1sq==w2sq:
          mode=MODE_wnid
          continue
        w=Wire(wnod,w1sq,w2sq)
        wires.add(w)
        popnp(0,0,w)
        span=w.span()
        print "Span",span
        if span is None:
          for i in tiles.layers:
            i.dirty=True
        else:
          tiles.layerid(span).dirty=True
        #save()
        w1sq=None
        w2sq=None
        mode=MODE_idle

    if event.type == pygame.MOUSEMOTION:
      crsq=translate((event.pos[0]/gw),(event.pos[1]/gw),tl)
      crnd=translate(((event.pos[0]+(gw/2))/gw),((event.pos[1]+(gw/2))/gw),tl)
      if mode in [MODE_addtx,MODE_addpn,MODE_addpu,MODE_addlb]:
        plsq=translate((event.pos[0]/gw),(event.pos[1]/gw),tl)
        #print plsq
      if mode==MODE_wire1:
        w1sq=translate(((event.pos[0]+(gw/2))/gw),((event.pos[1]+(gw/2))/gw),tl)
        #print w1sq
      if mode==MODE_wire2:
        step=math.radians(45)
        w2sqt=translate(((event.pos[0]+(gw/2))/gw),((event.pos[1]+(gw/2))/gw),tl)
        dx=w2sqt[0]-w1sq[0]
        dy=w2sqt[1]-w1sq[1]
        sdx=1 if dx>0 else -1
        sdy=1 if dy>0 else -1
        dt=math.sqrt(dx*dx+dy*dy)
        if dt!=0:
          if abs(dx/dt)<0.5:
            dx=0
          elif abs(dy/dt)<0.5:
            dy=0
          else:
            dx,dy=sdx*int(dt/math.sqrt(2)+0.5),sdy*int(dt/math.sqrt(2)+0.5)

          w2sq=(w1sq[0]+dx,w1sq[1]+dy)
        else:
          w2sq=w1sq

    screen.fill((0,0,0))
    render()
    pygame.display.flip()
    clock.tick(60)