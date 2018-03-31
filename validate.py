from collections import defaultdict
import os
import json

import PIL
import PIL.Image
import PIL.ImageFont
import PIL.ImageOps
import PIL.ImageDraw

PIXEL_ON = 0  # PIL color to use for "on"
PIXEL_OFF = 255  # PIL color to use for "off"


pullfiles=dict()

schpulls=set()
schnets=set()
schtransistors=dict()

netpulls=set()
netnets=set()
nettransistors=dict()

tcon=0
pue=0
txe=0

print "========  Transistor conflicts  ========"
for fn in os.listdir('layers'):
    with open(os.path.join('layers',fn),'r') as f:
      for line in f:
        if line[0]=='T':
          if line.split(':')[1]=='U':
            schpulls.add(int(line.split(':')[2].split(',')[0]))
            pullfiles[int(line.split(':')[2].split(',')[0])]=fn
          if line.split(':')[1]=='T':
            tpar=line.split(':')[2].split(',')
            if int(tpar[0]) in schtransistors:
              if (int(tpar[3]),min(int(tpar[2]),int(tpar[4])),max(int(tpar[2]),int(tpar[4])))!=(schtransistors[int(tpar[0])][0],schtransistors[int(tpar[0])][1],schtransistors[int(tpar[0])][2]):
                print 'ERROR: conflicting',tpar[0]+':',(int(tpar[3]),min(int(tpar[2]),int(tpar[4])),max(int(tpar[2]),int(tpar[4])),fn),schtransistors[int(tpar[0])]
                tcon+=1
            schtransistors[int(tpar[0])]=(int(tpar[3]),min(int(tpar[2]),int(tpar[4])),max(int(tpar[2]),int(tpar[4])),fn)
            schnets.add(int(tpar[2]))
            schnets.add(int(tpar[3]))
            schnets.add(int(tpar[4]))

with open('transdefs.js','r') as f:
  for i in json.load(f):
    nettransistors[int(i[0][1:])]=(i[1],min(i[2],i[3]),max(i[2],i[3]))
    netnets.add(i[1])
    netnets.add(i[2])
    netnets.add(i[3])
with open('segdefs.js','r') as f:
  for i in json.load(f):
    if i[1]=='+':
      netpulls.add(i[0])

print "===========  Pullup  errors  ==========="
for i in schpulls-netpulls:
  print "ERROR: incorrect pullup on node",i,"in file",pullfiles[i]
  pue+=1

print "=========  Transistor  errors  ========="
for i in schtransistors:
  if nettransistors[i][0]!=schtransistors[i][0] or nettransistors[i][1]!=schtransistors[i][1] or nettransistors[i][2]!=schtransistors[i][2]:
    print "ERROR: incorrect transistor",i,"in file",schtransistors[i][3]
    txe+=1
print "==============  Summary  ==============="
print "Transistor conflicts:    ",tcon
print "Pullup errors:           ",pue
print "Transistor errors:       ",txe
print "Nets implemented:       ",'%4d/%4d (%3d%%)'%(len(schnets),len(netnets),100*len(schnets)/len(netnets))
print "Pullups implemented:    ",'%4d/%4d (%3d%%)'%(len(schpulls),len(netpulls),100*len(schpulls)/len(netpulls))
print "Transistors implemented:",'%4d/%4d (%3d%%)'%(len(schtransistors),len(nettransistors),100*len(schtransistors)/len(nettransistors))

font = PIL.ImageFont.truetype('cour.ttf', size=20)
image = PIL.Image.new('RGB', (300,185), color=(255,255,255))
draw = PIL.ImageDraw.Draw(image)
draw.text((0,0), "Transistor conflicts:",fill=(0,0,0),font=font)
draw.text((280,0), str(tcon),fill=(0,255,0) if tcon==0 else (255,0,0),font=font)
draw.text((0,20),"Pullup errors:",fill=(0,0,0),font=font)
draw.text((280,20), str(pue),fill=(0,255,0) if pue==0 else (255,0,0),font=font)
draw.text((0,40),"Transistor errors:",fill=(0,0,0),font=font)
draw.text((280,40), str(txe),fill=(0,255,0) if txe==0 else (255,0,0),font=font)
draw.text((0,60),"Nets progress:",fill=(0,0,0),font=font)
draw.rectangle((0,82,300*len(schnets)/len(netnets),102),(192,255,192))
draw.text((0,80),"%3d%% (%4d/%4d)"%(100*len(schnets)/len(netnets),len(schnets),len(netnets)),fill=(0,0,0),font=font)
draw.text((0,100),"Pullups progress:",fill=(0,0,0),font=font)
draw.rectangle((0,122,300*len(schpulls)/len(netpulls),142),(192,255,192))
draw.text((0,120),"%3d%% (%4d/%4d)"%(100*len(schpulls)/len(netpulls),len(schpulls),len(netpulls)),fill=(0,0,0),font=font)
draw.text((0,140),"Transistorss progress:",fill=(0,0,0),font=font)
draw.rectangle((0,162,300*len(schtransistors)/len(nettransistors),182),(192,255,192))
draw.text((0,160),"%3d%% (%4d/%4d)"%(100*len(schtransistors)/len(nettransistors),len(schtransistors),len(nettransistors)),fill=(0,0,0),font=font)
image.save('status.png')