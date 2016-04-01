# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 10:30:36 2016

@author: lenovo
"""

import os
from pydub import AudioSegment,silence
from pydub.utils import mediainfo


os.chdir(os.path.dirname(os.path.realpath(__file__)))


def test_small():
    '''
    
    Должно получиться (но не выходит)
    <SpeechSegment ch="1" stime="26.20" etime="45.37" lang="eng" tconf="0.91">
<Word id="60" stime="26.50" dur="0.13" conf="0.990"> the </Word>
<Word id="61" stime="26.63" dur="0.24" conf="0.990"> person </Word>
<Word id="62" stime="26.93" dur="0.12" conf="0.990"> who </Word>
<Word id="63" stime="27.05" dur="0.22" conf="0.990"> dealt </Word>
<Word id="64" stime="27.27" dur="0.14" conf="0.990"> with </Word>
<Word id="65" stime="27.44" dur="0.25" conf="0.990"> me </Word>
<Word id="66" stime="27.82" dur="0.26" conf="0.990"> was </Word>
<Word id="67" stime="28.13" dur="0.21" conf="0.990"> really </Word>
<Word id="68" stime="28.50" dur="0.65" conf="0.990"> professional </Word>
<Word id="69" stime="29.62" dur="0.18" conf="0.990"> he </Word>
<Word id="70" stime="29.80" dur="0.22" conf="0.990"> helped </Word>
    
    '''
    inFile = r'Input_audio\0f57e594-09db-4642-8d9b-89cdf5e7424f.mp3'  #2-й файл в списке
    outFile=r'Output_audio\0f57e594-09db-4642-8d9b-89cdf5e7424f_part.mp3'
    sound = AudioSegment.from_mp3(inFile)
    original_bitrate = mediainfo(inFile)['bit_rate']
    segment = sound[26.50-26.20:(29.80+0.22-26.20)*1000]  #26.20 начало сегмента
    segment.export(outFile, format="mp3", bitrate=original_bitrate)
    
    
def test_joined():
    '''
    Должно получиться (и получается) :  
<Word id="6684" stime="4731.52" dur="0.19" conf="0.990"> the </Word>
<Word id="6685" stime="4731.77" dur="0.11" conf="0.990"> the </Word>
<Word id="6686" stime="4731.88" dur="0.31" conf="0.990"> lady </Word>
<Word id="6687" stime="4732.22" dur="0.13" conf="0.990"> that </Word>
<Word id="6688" stime="4732.38" dur="0.11" conf="0.990"> i </Word>
<Word id="6689" stime="4732.56" dur="0.22" conf="0.990"> spoke </Word>
<Word id="6690" stime="4732.84" dur="0.14" conf="0.990"> to </Word>
<Word id="6691" stime="4733.02" dur="0.17" conf="0.990"> was </Word>
<Word id="6692" stime="4733.23" dur="0.23" conf="0.990"> really </Word>
<Word id="6693" stime="4733.46" dur="0.62" conf="0.990"> helpful </Word>
    '''
    inFile = r'Joined.mp3' 
    outFile=r'Output_audio\part_from_joined.mp3'
    sound = AudioSegment.from_mp3(inFile)
    original_bitrate = mediainfo(inFile)['bit_rate']
    segment = sound[4731.52*1000:(4733.46+0.62)*1000]
    segment.export(outFile, format="mp3", bitrate=original_bitrate)


def findSegment(srcSeg, seekSeg, delta=0):
    lenSrcSeg = len(srcSeg)
    lenSeekSeg=len(seekSeg)
    if not srcSeg or not seekSeg or lenSeekSeg>lenSrcSeg:
        raise Exception('invalid args')
    seekTo = lenSrcSeg-lenSeekSeg+1
    for i in range(seekTo):
        audio_slice = srcSeg[i:i+lenSeekSeg]
        if audio_slice.rms==seekSeg.rms:
            return [i,i+lenSeekSeg]
        #for s in audio_slice
        #  delta_test=
    return []

def testFind():
        '''
    Вырезаем из joined.mp3 фрагмент и ищем по уровню сигнала этот же фрагмет в  0f57e594-09db-4642-8d9b-89cdf5e7424f.mp3
   Характеристики joined.mp3:
          Duration: 01:23:23.35, start: 0.138125, bitrate: 64 kb/s
            Stream #0:0: Audio: mp3, 8000 Hz, mono, s16p, 64 kb/s
            Metadata:
              encoder         : LAME3.98r
            Side data:   
                
   Характеристики  0f57e594-09db-4642-8d9b-89cdf5e7424f.mp3:
    Duration: 00:00:21.74, start: 0.138125, bitrate: 64 kb/s
    Stream #0:0: Audio: mp3, 8000 Hz, mono, s16p, 64 kb/s
    Metadata:
      encoder         : LAME3.98r
    Side data:
   Должно получиться (получается)
    <SpeechSegment ch="1" stime="26.20" etime="45.37" lang="eng" tconf="0.91">
<Word id="60" stime="26.50" dur="0.13" conf="0.990"> the </Word>
<Word id="61" stime="26.63" dur="0.24" conf="0.990"> person </Word>
<Word id="62" stime="26.93" dur="0.12" conf="0.990"> who </Word>
<Word id="63" stime="27.05" dur="0.22" conf="0.990"> dealt </Word>
<Word id="64" stime="27.27" dur="0.14" conf="0.990"> with </Word>
<Word id="65" stime="27.44" dur="0.25" conf="0.990"> me </Word>
<Word id="66" stime="27.82" dur="0.26" conf="0.990"> was </Word>
<Word id="67" stime="28.13" dur="0.21" conf="0.990"> really </Word>
<Word id="68" stime="28.50" dur="0.65" conf="0.990"> professional </Word>
<Word id="69" stime="29.62" dur="0.18" conf="0.990"> he </Word>
<Word id="70" stime="29.80" dur="0.22" conf="0.990"> helped </Word>
    
    '''
    fromFile     = r'Joined.mp3' 
    sound = AudioSegment.from_mp3(fromFile)
    search = sound[26.50*1000:(29.80+0.22)*1000]
    
    seekInFile =  r'Input_audio\0f57e594-09db-4642-8d9b-89cdf5e7424f.mp3'
    src = AudioSegment.from_mp3(seekInFile)
    original_bitrate = mediainfo(seekInFile)['bit_rate']
    r =findSegment(src, search )
    e = src[r[0]:r[1]]
    e.export(r'Output_audio\part_from_seek.mp3', format="mp3", bitrate=original_bitrate)
    
testFind()
    
#test_small()
#test_joined()