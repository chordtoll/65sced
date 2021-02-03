#!/usr/bin/env python
import json
class Node():
  def __init__(self,name,comment,number):
    self.names=[name]
    self.comments=[comment]
    self.nc=[(name,comment)]
    self.id=number
    self.pull=''
    self.gate=[]
    self.con=[]
  def addnc(self,name,comment):
    if name.replace('~','#') in self.names:
      return
    self.names.append(name)
    self.comments.append(comment)
    self.nc.append((name,comment))
  def addpull(self,pull):
    if self.pull=='':
      self.pull=pull
    assert self.pull==pull
  def addgate(self,gate):
    assert gate not in self.gate
    self.gate.append(gate)
  def addcon(self,con):
    assert con not in self.con
    self.con.append(con)
  def __repr__(self):
    return 'N%d :'%self.id+''.join(['\n\t%s // %s'%(i) for i in self.nc])
nodes = {}
transistors = {}

def findnode(name):
  for i in list(nodes.values()):
    if name.lower() in [n.lower() for n in i.names]:
      return i.id

def nodename(n):
  return ','.join(nodes[n].names)
def nodename1(n):
  return nodes[n].names[0]
def nodecom(n):
  return ','.join(nodes[n].comments)
def gatename(t):
  return nodename(transistors[t][0])
def gatecom(t):
  return nodecom(transistors[t][0])
def gateid(t):
  return transistors[t][0]
def otcname(t,n):
  if n==transistors[t][1]:
    return nodename(transistors[t][2])
  return nodename(transistors[t][1])
def otcid(t,n):
  if n==transistors[t][1]:
    return transistors[t][2]
  return transistors[t][1]

def tnname(t,i):
  return nodename(transistors[t][i])
def tncom(t,i):
  return nodecom(transistors[t][i])
def tnid(t,i):
  return transistors[t][i]

class Path():
  def __init__(self):
    self.seen=[]
  def search(self,n,depth=2):
    self.seen.append(n)
    nor=[]
    for t in nodes[n].con:
      if otcid(t,n)==558:
        nor.append(gatename(t))
      elif otcid(t,n) not in self.seen:
        search=self.search(otcid(t,n))
        if search!='()':
            nor.append("%s&%s"%(gatename(t),search))
    return "(%s)"%("|".join(nor))

def pathtoground(n):
  if nodes[n].pull=='-':
    return "No pullup"
  p=Path()
  return "~%s"%p.search(n)

with open('nodenames.js') as f:
  for line in f:
    if ('//' in line and ':' not in line.split('//')[0]) or ('//' not in line and ':' not in line):
      #print "NO :"
      continue
    name=line.split(':')[0].lstrip('"').rstrip('"')
    number=int(line.split(':')[1].split(',')[0])
    comment=line.split('//')[1].lstrip().rstrip() if '//' in line else ''
    if number not in nodes:
      nodes[number]=Node(name,comment,number)
    else:
      nodes[number].addnc(name,comment)
with open('segdefs.js') as f:
  a=json.load(f)
  for i in a:
    if i[0] not in nodes:
      nodes[i[0]]=Node('n%d'%i[0],"UNNAMED",i[0])
    nodes[i[0]].addpull(i[1])


with open('transdefs.js') as f:
  a=json.load(f)
  for i in a:
    if i[2]==i[3]:
      continue
    if i[2]>i[3]:
      i[2],i[3]=i[3],i[2]
    if i[1:4] in list(transistors.values()):
      continue
    transistors[int(i[0][1:])]=i[1:4]
    nodes[i[1]].addgate(int(i[0][1:]))
    nodes[i[2]].addcon(int(i[0][1:]))
    nodes[i[3]].addcon(int(i[0][1:]))

def genpla():
  for p in range(131):
    #print p
    for n in list(nodes.values()):
      for c in n.nc:
        if c[1]=='pla%d'%p:
          #print n
          bitfield=['X']*8
          t='         '
          tc='X'
          cck='          '
          pp='              '
          for i in n.con:
            if gatename(i)=='irline3':
              bitfield[0]='0'
              bitfield[1]='0'
            elif gatename(i).startswith('ir'):
              bitfield[int(gatename(i)[2])]='0'
            elif gatename(i).startswith('notir'):
              bitfield[int(gatename(i)[5])]='1'
            elif gatename(i) in ['t2','t3','t4','t5']:
              t=' & (t==%s)'%gatename(i)[1]
              tc=gatename(i)[1]
            elif gatename(i) in ['clock1','clock2']:
              t=' & (t==%i)'%(int(gatename(i)[-1])-1)#clock=' & (!%s)'%gatename(i)
              tc=str(int(gatename(i)[-1])-1)
            elif gatename(i) in ['cclk']:
              cck=' & (!%s)'%gatename(i)
            elif gatename(i) in ['x-op-push/pull']:
              pp=' & (!PLA[121])'
            elif gatename(i) in ['op-push/pull']:
              pp=' & (!PLA[ 97])'
            elif gatename(i) in ['n603']:
              pp=' & (!n603    )'
            else:
              print(gatename(i))
          print('PLA[%3d] = (ir=?=8\'b%s)' %(p,''.join(bitfield[::-1]))+t+cck+pp+'; // %4d:%s'%(n.id,c[0]))
          #print '%3d %s %s'%(p,''.join(bitfield[::-1]),tc)+(' !' if pp.rstrip()!='' else '')
          found=True
'''genpla()

'''
if __name__=="__main__":
  while True:
    query=input("Node id:")
    if query[0:2]=='.t':
      print('Gate: %10s (%4d) \t//%s'%(tnname(int(query[2:]),0),tnid(int(query[2:]),0),tncom(int(query[2:]),0)))
      print('Node: %10s (%4d) \t//%s'%(tnname(int(query[2:]),1),tnid(int(query[2:]),1),tncom(int(query[2:]),1)))
      print('Node: %10s (%4d) \t//%s'%(tnname(int(query[2:]),2),tnid(int(query[2:]),2),tncom(int(query[2:]),2)))
      continue
    try:
      nid=int(query)
    except:
      nid=findnode(query)
    node=nodes[nid]
    print(node)
    print("\t"+pathtoground(nid))
    print("\tTXRS:")
    for i in node.con:
      if otcid(i,nid)==558:
        print("\t\t!%s (!%i) : %i \t//%s"%(gatename(i),gateid(i),i,gatecom(i)))
      else:
          print("\t\t%s->%s (%i->%i) : %i"%(gatename(i),otcname(i,nid),gateid(i),otcid(i,nid),i))
    print("\tGATE:")
    for i in node.gate:
      if tnid(i,1)==558:
        print("\t\t!->%s (!%i) : %i \t//%s"%(tnname(i,2),tnid(i,2),i,tncom(i,1)))
      elif tnid(i,2)==558:
        print("\t\t!->%s (!%i) : %i \t//%s"%(tnname(i,1),tnid(i,1),i,tncom(i,1)))
      else:
        print("\t\t%s--%s (%i--%i) : %i "%(tnname(i,1),tnname(i,2),tnid(i,1),tnid(i,2),i))
  ''''''