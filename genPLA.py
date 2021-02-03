#!/usr/bin/env python

import bisect
widths=[47]+[100]*10
ranges=[(6,21),(21,37),(37,53),(53,73),(73,91),(91,105),(105,120),(120,131)]
attrs={2:{'x':91,'w':47,'i':11,'r':(6,21)}}
for i in range(3,10):
  attrs[i]={'w':3*(ranges[i-2][1]-ranges[i-2][0])+2,'i':9+i,'r':ranges[i-2]}
for i in range(3,10):
  attrs[i]['x']=attrs[i-1]['x']+attrs[i-1]['w']+2

tyd={'t5':9,'t4':9,'t3':9,'t2':9,'clock2':9,'clock1':9,'irline3':12}
twd={'t5':3,'t4':4,'t3':5,'t2':6,'clock2':7,'clock1':8,'irline3':11}
for i in range(0,8):
  #print "tyd['ir%i']=%i"%(i,16+(7-i)*4)
  tyd['ir%i'%i]=16+(7-i)*4
  twd['ir%i'%i]=15+(7-i)*4
  #print "tyd['notir%i']=%i"%(i,16+(7-i)*4)
  tyd['notir%i'%i]=16+(7-i)*4
  twd['notir%i'%i]=14+(7-i)*4
revtwd={v:k for k,v in list(twd.items())}


for blk in range(2,10):
  with open('layers/nPLA%i.sch'%blk,'w') as f:

    ba=attrs[blk]
    f.write("#PLA%i,%i,2,%i,50,%i\n"%(blk,ba['x'],ba['w'],ba['i']))
    layerid=ba['i']
    import decodePLA
    xyid={twd[y]:[] for y in list(twd.keys())}
    for i in range(ba['r'][0],ba['r'][1]):
      cyid=[2,(46 if i%2==0 else 47)]
      nid=decodePLA.findnode('pla%i'%i)
      f.write("T%i,%i:L:%i,0\n"%(2+(i-ba['r'][0])*3,(46 if i%2==0 else 47),nid))
      f.write("T%i,0:U:%i,2\n"%(2+(i-ba['r'][0])*3,nid))
      #print 'pla%i:%i'%(i,nid)
      node=decodePLA.nodes[nid]
      for c in node.con:
        if decodePLA.otcid(c,nid)==558:
          #print "\t\t!%s (!%i) : %i"%(decodePLA.gatename(c),decodePLA.gateid(c),c)
          if decodePLA.gatename(c) in tyd:
            #print "TXR.y=",tyd[decodePLA.gatename(c)] 
            #print "TXR.x=",1+(i-6)*3
            bisect.insort(cyid,tyd[decodePLA.gatename(c)]+1)
            bisect.insort(xyid[twd[decodePLA.gatename(c)]],2+(i-ba['r'][0])*3)
            f.write("T%i,%i:T:%i,0,558,%i,%i\n"%(1+(i-ba['r'][0])*3,tyd[decodePLA.gatename(c)],c,decodePLA.gateid(c),nid))
            f.write("W%i,%i,%i:%i,%i,%i:%i\n"%(2+(i-ba['r'][0])*3,tyd[decodePLA.gatename(c)],layerid,2+(i-ba['r'][0])*3,twd[decodePLA.gatename(c)],layerid,decodePLA.gateid(c)))
      for v,w in zip(cyid, cyid[1:]):
        f.write("W%i,%i,%i:%i,%i,%i:%i\n"%(3+(i-ba['r'][0])*3,v,layerid,3+(i-ba['r'][0])*3,w,layerid,nid))
      print(twd,'\n',revtwd,'\n')
      for y in list(xyid.keys()):
        for v,w in zip(xyid[y], xyid[y][1:]):
          print(v,w,y,decodePLA.findnode(revtwd[y]))
          f.write("W%i,%i,%i:%i,%i,%i:%i\n"%(v,y,layerid,w,y,layerid,decodePLA.findnode(revtwd[y])))