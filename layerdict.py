class LayerDict():
  def __init__(self):
    self.layers=[]
    self.ids=[]
  def addlayer(self,name,x1,y1,x2,y2,lid=-1):
    if lid==-1:
      if self.ids:
        lid=max(self.ids)+1
      else:
        lid=0
    l=Layer(name,x1,y1,x2,y2,lid)
    print l
    for i in self.layers:
      print '\t',i
      assert not i.overlaps(l)
    assert lid not in self.ids
    self.layers.append(l)
    self.ids.append(lid)
  def albb(self):
    return (min([i.x1 for i in self.layers]),max([i.x2 for i in self.layers]),min([i.y1 for i in self.layers]),max([i.y2 for i in self.layers]))

  def rects(self):
    for i in self.layers:
      yield ((i.x1,i.y1),(i.x2,i.y2),i)
  def layerat(self,x,y):
    for i in self.layers:
      if i.contains(x,y):
        return i
    return None
  def layerid(self,g):
    for i in self.layers:
      if i.id==g:
        return i
    return None
  def xy2xyg(self,x,y):
    l=self.layerat(x,y)
    g=l.id
    x-=l.x1
    y-=l.y1
    return x,y,g
  def xyg2xy(self,x,y,g):
    l=self.layerid(g)
    x+=l.x1
    y+=l.y1
    return x,y
  def __getitem__(self,key):
    x,y=key
    l=self.layerat(x,y)
    if l:
      return l.getglobal(x,y)
    raise KeyError
  def __setitem__(self,key,value):
    x,y=key
    l=self.layerat(x,y)
    if l:
      l.setglobal(x,y,value)
    else:
      raise KeyError
  def __delitem__(self,key):
    x,y=key
    l=self.layerat(x,y)
    if l:
      l.delglobal(x,y)
    else:
      raise KeyError
  def __contains__(self,key):
    x,y=key
    l=self.layerat(x,y)
    if l:
      return l.containsglobal(x,y)
    else:
      return False
  def __iter__(self):
    for l in self.layers:
      for t in l:
        yield t
class Layer():
  def __init__(self,name,x1,y1,x2,y2,lid):
    self.dict={}
    self.name=name
    self.x1=min(x1,x2)
    self.y1=min(y1,y2)
    self.x2=max(x1,x2)
    self.y2=max(y1,y2)
    self.id=lid
    self.dirty=True
  def __repr__(self):
    return "%s: (%d,%d)-(%d,%d)"%(self.name,self.x1,self.y1,self.x2,self.y2)
  def contains(self,x,y):
    return x>=self.x1 and x<self.x2 and y>=self.y1 and y<self.y2
  def overlaps(self,layer):
    if self.x1>=layer.x2 or layer.x1>=self.x2:
      return False
    if self.y1>=layer.y2 or layer.y1>=self.y2:
      return False
    return True
  def getglobal(self,x,y):
    return self.dict[(x-self.x1,y-self.y1)]
  def setglobal(self,x,y,value):
    self.dict[(x-self.x1,y-self.y1)]=value
    self.dirty=True
  def delglobal(self,x,y):
    del self.dict[(x-self.x1,y-self.y1)]
    self.dirty=True
  def containsglobal(self,x,y):
    return (x-self.x1,y-self.y1) in self.dict
  def __iter__(self):
    for x,y in self.dict:
      yield x+self.x1,y+self.y1 
