# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 20:19:09 2016

@author: lenovo
"""
import os
from pydub import AudioSegment,silence
from pydub.utils import mediainfo


os.chdir(os.path.dirname(os.path.realpath(__file__)))
import matplotlib.pyplot as plt
#plt.plot([1,2,3,4], [1,4,9,16], 'ro')
#plt.axis([0, 6, 0, 20])
#plt.show()()
def  log(msg):
    f = open('plot.log', 'a')
    f.write(msg+"\n")
    f.close()    
    
def calcPlot(segment, step=100):
    seg1Len = len(segment)
    x=[]
    y=[]
    l =  seg1Len//step
    for i in range(0,l):
        fr =  i*step;
        to = (i+1)*step
        s1 = segment[fr:to]
        x.append((fr+to)//2)
        y.append(s1.rms)        
    x.append((l*step+seg1Len)//2)    
    y.append(segment[l*step:seg1Len].rms)
    return x,y 

def logRms(segment, step=100):
    seg1Len = len(segment)
    l =  seg1Len//step
    for i in range(0,l):
        fr =  i*step;
        to = (i+1)*step
        s1 = segment[fr:to]
        log('fr={0};to={1};avr={2};rms={3}'.format(fr,to, (fr+to)//2, s1.rms))

    log('fr={0};to={1};avr={2};rms={3}'.format(l*step,seg1Len, (l*step+seg1Len)//2, segment[l*step:seg1Len].rms))    
 

def showPlot():   
    src= AudioSegment.from_mp3(r'Output_audio\part_from_join.mp3')
    x,y = calcPlot(src)
    plt.figure(0)
    plt.plot(x, y)
    plt.xlabel('part_from_join.mp3')
    #plt.axis([0, 6, 0, 20])
    
    
    
    plt.figure(1) 
    src= AudioSegment.from_mp3(r'Input_audio\1bdcf42e-1bdb-4058-b9e5-6ee670ec509b.mp3')
    x,y = calcPlot(src)
    plt.plot(x, y)
    plt.xlabel('1bdcf42e-1bdb-4058-b9e5-6ee670ec509b.mp3')
    #plt.axis([0, 6, 0, 20])
    plt.show()() 

def logData():  
    src= AudioSegment.from_mp3(r'Output_audio\part_from_join.mp3') 
    log(r'Output_audio\part_from_join.mp3') 
    logRms(src)
    log('---------')
    src= AudioSegment.from_mp3(r'Input_audio\1bdcf42e-1bdb-4058-b9e5-6ee670ec509b.mp3')
    log(r'Input_audio\1bdcf42e-1bdb-4058-b9e5-6ee670ec509b.mp3')
    logRms(src)
    log('---------')
'''    
def compareSegments(srcSeg,fr_,to_,seekSeg, step=100, threshold):
    srcSeg1Len = to_- fr_
    seekSegLen = len(seekSeg)
    if seekSegLen!=srcSeg1Len:
         raise Exception('invalid args')
    l =  srcSeg1Len//step
    
    for i in range(0,l):
        fr =  i*step;
        to = (i+1)*step
        s1 = srcSeg1Len[fr:to]
        s2 = seekSegLen[fr:to]
        if s1.rms!=s2.rms:
            return False
    if  seg1[l*step:seg1Len].rms!=seg2[l*step:seg2Len].rms:
        return False       
    return True             

def findSegment(srcSeg, seekSeg):
    lenSrcSeg = len(srcSeg)
    lenSeekSeg=len(seekSeg)
    
    if not srcSeg or not seekSeg or lenSeekSeg>lenSrcSeg:
        raise Exception('invalid args')
    seekTo = lenSrcSeg-lenSeekSeg+1
    for i in range(seekTo):
        audio_slice = srcSeg[i:i+lenSeekSeg]
        if compareSegments(srcSeg,i,i+lenSeekSeg,seekSeg):
            return [i,i+lenSeekSeg]
    return []   
    
'''    

def compareSound(src, msFrom, msTill, seek, step=100):
    lenSrcSeg = msTill - msFrom
    lenSeek = len(seek)
    if not src or not seek or lenSeek>lenSrcSeg:
        raise Exception('invalid args')
    l =  lenSrcSeg//step
    r =  lenSrcSeg%step   
    
    for i in range(0, l, step):
        fr =  int(i*step);
        to = int((i+1)*step) 
        segSrc = src[msFrom+fr:msFrom+to]
        segSeek= seek[fr, to]
        if segSrc.rms!=segSeek.rms:
            return False
    #TODO:остаток
    return True    
    
def findSound(src, msFrom, msTill, seek):
    lenSrcSeg = msTill - msFrom
    lenSeek = len(seek)
    if not src or not seek or lenSeek>lenSrcSeg:
        raise Exception('invalid args')
    seekTo = msTill-lenSeek+1
    for i in range(msFrom, seekTo):
        if compareSound(src,i,i+lenSeek,seek):
            return [i,i+lenSeek]
    return [] 

def test1():
    src= AudioSegment.from_mp3(r'Input_audio\1bdcf42e-1bdb-4058-b9e5-6ee670ec509b.mp3')
    l = len(src)
    seek= AudioSegment.from_mp3(r'Input_audio\1bdcf42e-1bdb-4058-b9e5-6ee670ec509b.mp3')
    r = findSound(src, 0, l, seek)
    if r!=[0, l]:
        raise Exception('test1 not passed')
    return True    

test1()    
   
        
    