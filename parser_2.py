# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 10:48:51 2016

@author: lenovo
"""

from pydub import AudioSegment,silence
from pydub.utils import mediainfo
import os

def log(msg):
     f = open('parser.log', 'w')
     f.write(msg+"\n")
     f.close()



''' soundLen = len(sound)
fr = 6*1000
to = 15*1000    
minSoundLen = 10*1000
minSilenceLen=500
silenceThresh=-50
if soundLen < minSoundLen:
    log('sound is less then {0} msec'.format(minSoundLen))
    return []
if soundLen < to:
    log('sound  is less then {0} msec'.format(to))
    return []
segment = sound[fr:to]'''         

def findSilence(segment):    
    minSilenceLen=500
    silenceThresh=-50
    silenceSegmentsList = silence.detect_silence(segment, min_silence_len=minSilenceLen, silence_thresh=silenceThresh)
    if len(silenceSegmentsList)==0:
         log('not found silence segments with min_silence_len={0} and silence_thresh={1}'.format(minSilenceLen,silenceThresh))
         return 0
    return   (silenceSegmentsList[-1][0]+silenceSegmentsList[-1][1])//2
     

def getFileName( fileName=''):
    fileName = os.path.basename(fileName)
    return trimExt(fileName)

def trimExt( fileName=''):
    return    os.path.splitext(fileName)[0] 
    
def cutMp3(inFile,outDir):
     log('Begin work with file '+ inFile)
     sound = AudioSegment.from_mp3(inFile)
     original_bitrate = mediainfo(inFile)['bit_rate']
     soundLen = len(sound)
     fr = 6*1000
     to = 15*1000    
     minSoundLen = 10*1000
     if soundLen < minSoundLen:
         log("\t sound is less then {0} msec".format(minSoundLen))
         return 0
     if soundLen < to:
         log("\t sound  is less then {0} msec".format(to))
         return [] 
     #cut = findSilence(sound[fr:to])
     #TempOutputFileName = trimExt(inFile)+'(1).mp3'
     #sound[0:cut].export(TempOutputFileName, format="mp3", bitrate=original_bitrate)
     timeLeft = soundLen
     count = 1
     begin = 0
     while timeLeft >= minSoundLen:
         cut = findSilence(sound[begin+fr:begin+to])
         soundToWrite = sound[begin:begin+cut]
         soundLeft = sound[cut+1:soundLen]         
         TempOutputFileName = '{0}({1})_{2}_{3}.mp3'.format(getFileName(inFile),count,begin,cut)
         soundToWrite.export(os.path.join(outDir,TempOutputFileName), format="mp3", bitrate=original_bitrate)
         begin = cut+1
         count+=1
         timeLeft = len(soundLeft) 
        

def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    inFile=r'Input_audio\0a94028e-c665-4c37-ac72-b40ae830aa97.mp3'
    outDir=r'Output_audio'
   
    cutMp3(inFile, outDir)
    print('ОК')

main()    