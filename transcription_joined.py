# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 14:26:01 2016

@author: lenovo
"""
import os
from pydub import AudioSegment,silence
from pydub.utils import mediainfo


os.chdir(os.path.dirname(os.path.realpath(__file__)))

def  log(msg):
    f = open('compare.log', 'a')
    f.write(msg+"\n")
    f.close()


def compareSegments(seg1,seg2, step=200):
    seg1Len = len(seg1)
    seg2Len = len(seg2)
    if seg1Len!=seg2Len:
         raise Exception('invalid args')
    l =  seg1Len//step
    for i in range(0,l):
        fr =  i*step;
        to = (i+1)*step
        s1 = seg1[fr:to]
        s2 = seg2[fr:to]
        #log('fr={0};to={1}'.format(fr,to))
        if s1.rms!=s2.rms:
            return False
    if  seg1[l*step:seg1Len].rms!=seg2[l*step:seg2Len].rms:
        return False
         
    #for i,j in zip(seg1,seg2):
    #    if i.rms!=j.rms: return False
        
    return True             

def findSegment(srcSeg, seekSeg, delta=0):
    lenSrcSeg = len(srcSeg)
    lenSeekSeg=len(seekSeg)
    
    if not srcSeg or not seekSeg or lenSeekSeg>lenSrcSeg:
        raise Exception('invalid args')
    seekTo = lenSrcSeg-lenSeekSeg+1
    for i in range(seekTo):
        audio_slice = srcSeg[i:i+lenSeekSeg]
        if compareSegments(audio_slice,seekSeg):
            return [i,i+lenSeekSeg]
        #for s in audio_slice
        #  delta_test=
    return []
    
    
    
    
def testFind():

   
    srcFile     = r'Joined.mp3' 
    src = AudioSegment.from_mp3(srcFile)
   
    
    seekFile =  r'Input_audio\0f57e594-09db-4642-8d9b-89cdf5e7424f.mp3'
    seek = AudioSegment.from_mp3(seekFile)
    original_bitrate = mediainfo(seekFile)['bit_rate']
    r =findSegment(src, seek )
    e = src[r[0]:r[1]]
    e.export(r'Output_audio\part_from_seek2.mp3', format="mp3", bitrate=original_bitrate)  
    print(r[0]/1000, r[1]/1000)

def testFind2():
    srcFile     =r'Input_audio\0f57e594-09db-4642-8d9b-89cdf5e7424f.mp3' 
    src = AudioSegment.from_mp3(srcFile)
   
    r =  compareSegments(src, src)
    print(r)
    
testFind()    