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

def cutMp3(inFile,outDir):
    sound = AudioSegment.from_mp3(inFile)
    soundLen = len(sound)
    fr = 6*1000
    to = 15*1000    
    minSoundLen = 10*1000
    minSilenceLen=300
    silenceThresh=-50
    if soundLen < minSoundLen:
        log('file "{0}" is less then {1} msec'.format(inFile,minSoundLen))
        return []
    if soundLen < to:
        log('file "{0}"  is less then {1} msec'.format(inFile,to))
        return []
    segment = sound[fr:to]
    silenceSegmentsList = silence.detect_silence(sound, min_silence_len=minSilenceLen, silence_thresh=silenceThresh)
    if len(silenceSegmentsList)==0:
         log('file "{0}": not found silence segments with min_silence_len={0} and silence_thresh={1}'.format(minSilenceLen,silenceThresh))
         return []
        

def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    inFile=r'Input_audio\0a94028e-c665-4c37-ac72-b40ae830aa97.mp3'
    cutMp3(inFile)

main()    