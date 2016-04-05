# -*- coding: utf-8 -*-
"""
Created on Sat Apr  2 14:26:01 2016

@author: lenovo
"""
import os
from pydub import AudioSegment,silence
from pydub.utils import mediainfo
import xml.sax
import pandas as pd
from math import sqrt
os.chdir(os.path.dirname(os.path.realpath(__file__)))
'''
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
        if compareSegments(audio_slice,seekSeg):
            return [i,i+lenSeekSeg]
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
'''    
#testFind() 
class ParseHandler(xml.sax.ContentHandler):    
    def __init__(self):
        self.words=[]
        
    def startElement(self, name, attrs):
        self._curentTag=name
        if self._curentTag == "Word":
            self._currentStime=float(attrs.get("stime"))*1000
            self._currentDur=float(attrs.get("dur"))*1000
        
    def characters(self, content):    
        if self._curentTag == "Word":
             self.words.append({'word':content.rstrip(), 'stime':self._currentStime,'dur':self._currentDur})
    

class SoundBase():
    def __init__(self):
        self.step=1000
        self.threshHold=200
    
    def findDeviation(self, src, msFrom, msTill, seek):
        lenSrcSeg = msTill - msFrom
        lenSeek = len(seek)
        if not src or not seek or lenSeek>lenSrcSeg:
            raise Exception('invalid args')
        l =  lenSrcSeg//self.step
        r =  lenSrcSeg%self.step   
        #log('----- compareSound --------')
        #llog=[]
        S2=0
        for i in range(0, l):
            fr =  int(i*self.step);
            to = int((i+1)*self.step) 
            segSrc = src[msFrom+fr:msFrom+to]
            segSeek= seek[fr:to]
            segSrcRms=segSrc.rms
            segSeekRms=segSeek.rms
            #log('cmp')
            #llog.append('    src: fr={0};to={1};rms={2}||seek: fr={3};to={4};rms={5} || delta={6}'.format(msFrom+fr,msFrom+to, segSrcRms,fr,to, segSeekRms, segSrcRms-segSeekRms))
            S2+= (segSrcRms-segSeekRms) *(segSrcRms-segSeekRms)      
            #log('    seek: fr={0};to={1};rms={2}'.format(fr,to, segSeek.rms))
            #if segSrc.rms!=segSeek.rms:
            #    return False
            
        #if  src[lenSrcSeg-r:lenSrcSeg].rms!=seek[lenSeek-r:lenSeek].rms:
        #s    return False 
        #log(' msFrom={0}, msTill={1}, D={2}'.format( msFrom, msTill, sqrt(S2)))  
        #log("\r\n".join(llog))    
        #D.append( sqrt(S2))    
        return sqrt(S2/l)    
        
    def findSound(self, src, msFrom, msTill, seek):
        lenSrcSeg = msTill - msFrom
        lenSeek = len(seek)
        if not src or not seek or lenSeek>lenSrcSeg:
            raise Exception('invalid args')
        seekTo = msTill-lenSeek+1
        D=[]
        I=[]
        for i in range(msFrom, seekTo):
            dev =  self.findDeviation(src,i,i+lenSeek,seek)
            if dev==0:
                return [i,i+lenSeek]
            D.append(dev)
            I.append({'from':i,'till':i+lenSeek})        
            #if findDeviation(src,i,i+lenSeek,seek):
            #    return [i,i+lenSeek]
        minD=min(D)    
        minDIndex = D.index(minD)
        if minD>self.threshHold:
            return []
        else:
            return [I[minDIndex]['from'], I[minDIndex]['till']]



class Cut(SoundBase):
    def __init__(self,words=[]):
        SoundBase.__init__(self)
        self.words = words
        self.currentMs=0
        self.joinedSoundLen=0
        self.logFile='parser.log'
        self.audioInDir = 'Input_audio'
        self.txtOutDir = 'Output_text'
        self.audioOutDir = 'Output_audio'
        self.noiseOutDir = 'Output_noise'
        self.fileNamesList=pd.read_csv('FileNames.csv')['Name'] 
        self.pathToJoined='Joined.mp3'
        self.joinedSound=[]
        self.currentSound=[]
        self.currentFile=''
   
    def  log(self,msg):
        f = open(self.logFile, 'a')
        f.write(msg+"\n")
        f.close()    
    
    def trimExt(self, fileName=''):
        return    os.path.splitext(fileName)[0]
        
    def run(self):
        self.joinedSound = AudioSegment.from_mp3(self.pathToJoined)
        self.joinedSoundLen=len(self.joinedSound)
        for file in self.fileNamesList:
            self.currentFile=self.trimExt(file)            
            path = os.path.join(self.audioInDir, file)
            self.processFile(path)
       
    

 
    
    def writeWords(self,fr,to):
        text=''        
        for index,word in enumerate(self.words):
            if word['stime']>=fr and (word['stime']+word['dur'])<to:
                text+=word['word']
                del self.words[index]
        self.log('file={0}'.format(self.currentFile))
        self.log(text)
        self.log('--------------')        
        
    def  processFile(self, path):
        self.currentSound = AudioSegment.from_mp3(path)
        self.step =len(self.currentSound)//10 
        foundSeg = self.findSound(self.joinedSound,  self.currentMs, self.currentMs+len(self.currentSound)*2, self.currentSound)
        if not foundSeg:
            self.log('Sound from file {0} is not found in {1}'.format(path,self.pathToJoined))
            return
        fr,till =  foundSeg
        #fr+=self.currentMs
        #to+=self.currentMs
        self.writeWords(fr,till)    
        self.currentMs = till+1   
        
'''        
def test():
    src =  AudioSegment.from_mp3('Joined.mp3')
    original_bitrate = mediainfo('Joined.mp3')['bit_rate']    
    
   # seek = AudioSegment.from_mp3(r'Input_audio\1bdcf42e-1bdb-4058-b9e5-6ee670ec509b.mp3')
    #c = Cut()
    #r = c.findSegment2(src, seek, int(44.88*1000))
    #print(r)
    src[44.00*1000:(100)*1000].export(r'Output_audio\part_from_join.mp3', format="mp3",bitrate=original_bitrate)


def test2():
    src= AudioSegment.from_mp3(r'Output_audio\part_from_join.mp3')
    seek =  AudioSegment.from_mp3(r'Input_audio\1bdcf42e-1bdb-4058-b9e5-6ee670ec509b.mp3')
    c = Cut()
    r = c.findSegment(src, seek)
    print(r)'''

def main():
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = ParseHandler()
    parser.setContentHandler(handler)
    parser.parse("full.xml")
    words = handler.words
    
    c = Cut(words)
    c.run()
    
   
main()   