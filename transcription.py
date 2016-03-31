# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 15:12:37 2016


"""
import os
from pydub import AudioSegment,silence
from pydub.utils import mediainfo


class Common():
     def __init__(self):
         self.logFile="parser.log"
         
     def  log(self,msg):
         f = open(self.logFile, 'a')
         f.write(msg+"\n")
         f.close()
         
     def getFileName(self, fileName=''):
         fileName = os.path.basename(fileName)
         return self.trimExt(fileName)
         
     def trimExt(self, fileName=''):
         return    os.path.splitext(fileName)[0]
     
     def forceDir(self, *dirs):
        for dir_ in dirs:
            if not os.path.exists(dir_):
                os.makedirs(dir_)
         
         
class CutMp3(Common):
     def __init__(self):
         Common.__init__(self)
         self.minTime = 6*1000
         self.maxTime = 15*1000    
         self.minSoundLen = 10*1000
         self.minSilenceLen=100
         self.silenceThresh=-60
         self.outDir='Output_audio' 
         self.forceDir(self.outDir)

     def findSilence(self,segment):    
         silenceSegmentsList = silence.detect_silence(segment, min_silence_len=self.minSilenceLen, silence_thresh=self.silenceThresh)
         if len(silenceSegmentsList)==0:
             self.log('not found silence segments with min_silence_len={0} and silence_thresh={1}'.format(self.minSilenceLen,self.silenceThresh))
             return 0
         return   (silenceSegmentsList[-1][0]+silenceSegmentsList[-1][1])//2  
         
     def writeFilePart(self, inFile, count, soundToWrite, original_bitrate):
         TempOutputFileName = '{0}({1}).mp3'.format(self.getFileName(inFile),count)
         soundToWrite.export(os.path.join(self.outDir,TempOutputFileName), format="mp3", bitrate=original_bitrate)
         self.log('    write file "{0}"'.format(TempOutputFileName))
         
     def cut(self,inFile):
         self.log('Begin work with file '+ inFile)
         sound = AudioSegment.from_mp3(inFile)
         original_bitrate = mediainfo(inFile)['bit_rate']
         soundLen = len(sound)         
         if soundLen < self.minSoundLen:
             self.log("   sound is less then {0} msec".format(self.minSoundLen))
             return 0
         if soundLen < self.maxTime:
             self.log("   sound  is less then {0} msec".format(self.maxTime))
             return 0 

         timeLeft = soundLen
         count = 1
         begin = 0
         while timeLeft >= self.minSoundLen:
             fr = begin+self.minTime
             if fr>soundLen:
                 self.log("   Error: out of bounds,  from={0} msec".format(fr))
                 break;         
             to = begin+self.maxTime
             if to>soundLen:
                 to = soundLen
             
             silence = self.findSilence(sound[fr:to])
             if not silence:
                 break
             cut = begin + silence
             soundToWrite = sound[begin:cut]              
             self.writeFilePart(inFile, count, soundToWrite, original_bitrate)
             
             begin = cut+1
             count+=1
             timeLeft = soundLen-(cut+1)             
        
         self.writeFilePart(inFile, count, sound[cut+1:soundLen], original_bitrate)
         self.log('    cut OK')
         return 1    
 


def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    inFile=r'Input_audio\2af9a4f1-0071-47da-91ad-22c2a024e443.mp3'
 
   
    #cutMp3(inFile, outDir)
   
    c = CutMp3()
    c.cut(inFile)
    
main()    
        