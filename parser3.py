# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 08:36:50 2016

@author: lenovo
"""

from pydub import AudioSegment,silence
from pydub.utils import mediainfo,db_to_float
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

def detect_silence(audio_segment, min_silence_len=1000, silence_thresh=-16):
    seg_len = len(audio_segment)

    # you can't have a silent portion of a sound that is longer than the sound
    if seg_len < min_silence_len:
        return []

    # convert silence threshold to a float value (so we can compare it to rms)
    silence_thresh = db_to_float(silence_thresh) * audio_segment.max_possible_amplitude

    # find silence and add start and end indicies to the to_cut list
    silence_starts = []

    # check every (1 sec by default) chunk of sound for silence
    slice_starts = seg_len - min_silence_len
    f = open('silence.log', 'w')
     
   

    for i in range(slice_starts + 1):
        audio_slice = audio_segment[i:i+min_silence_len]
        f.write("rms = {0}; thresh = {1}; sec = {2}   \n".format(audio_slice.rms, silence_thresh, i/1000))
        if audio_slice.rms < silence_thresh:
            silence_starts.append(i)
    f.close()        
    # short circuit when there is no silence
    if not silence_starts:
        return []

    # combine the silence we detected into ranges (start ms - end ms)
    silent_ranges = []

    prev_i = silence_starts.pop(0)
    current_range_start = prev_i

    for silence_start_i in silence_starts:
        if silence_start_i != prev_i + 1:
            silent_ranges.append([current_range_start,
                                  prev_i + min_silence_len])
            current_range_start = silence_start_i
        prev_i = silence_start_i

    silent_ranges.append([current_range_start,
                          prev_i + min_silence_len])

    return silent_ranges
def mp3Ripper(inFile, outFile, stime, etime):
     Sound = AudioSegment.from_mp3(inFile)
     original_bitrate = mediainfo(inFile)['bit_rate']
     SegmentSound = Sound[stime:etime]     
     SegmentSound.export(outFile, format="mp3", bitrate=original_bitrate)
     


    
     
def main():
    inFile=r'Input_audio\0a94028e-c665-4c37-ac72-b40ae830aa97.mp3'
    # outFile=r'Input_audio\0a94028e-c665-4c37-ac72-b40ae830aa97____test.mp3'
    #mp3Ripper(inFile, outFile, 5.60, 9.98)
    sound = AudioSegment.from_mp3(inFile)
    result= detect_silence(sound, min_silence_len=500, silence_thresh=-50)
    count=0;
    len_= len(result)-1
    
    for i in range(len_):
        
        if i!=len_:
            fr = round((result[i][0]+result[i][1])/2)
            to = round((result[i+1][0]+result[i+1][1])/2)
            outFile = r'silence\0a940_loud_{0}_{1}.mp3'.format( round(fr/1000,2), round(to/1000,2))
            mp3Ripper(inFile, outFile, fr, to)
        
        count +=1
        
        
    print(result)

main()     