# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 23:28:46 2016

@author: user
"""

import pandas as pd
import os
os.chdir('C:/PythonProjects\TakeNoneScript')
import re
from shutil import copyfile
from pydub import AudioSegment

def find_segment_list_begin(content):
    i=0
    while (i < len(content)):
        if content[i]=="<SegmentList>\n":
            return i
        i = i+1
    return 0

def find_segment_list_end(content):
    i=0
    while (i < len(content)):
        if content[i]=="</SegmentList>\n":
            return i
        i = i+1
    return 0

def get_speech_segment_range (content, start_line):
    i=start_line
    while (i < len(content)):
        if "<SpeechSegment " in content[i]:
            start_segment_line = i
            break
        else:
            i = i+1
            
    i = start_segment_line
    while (i < len(content)):
        if "</SpeechSegment" in content[i]:
            end_segment_line = i
            break
        else:
            i = i+1
    
    return start_segment_line, end_segment_line
    
def get_word(string):
    m = re.search('"> (.+?)</Word>', string)
    if m:
        s = m.group(1)
        return s.strip()
    return ''

def is_general_tag(string):
    if ('female/native' in string) or \
        ('male/native' in string) or \
        ('male/non-native' in string) or \
        ('female/non-native' in string) or \
        ('female/foreign–language' in string) or \
        ('male/foreign–language' in string):
        return True
    else:
        return False

def is_noise_tag(string):
    if ('bad-audio' in string) or \
        ('no-relevant-speech' in string):
        return True
    else:
        return False

def find_next_endoffile (content, start_line, ignore_first=False):
    i=start_line
    count = 0
    while (i < len(content)):
        s = get_word(content[i])
        if is_general_tag(s) or is_noise_tag(s):
            count = count + 1
        if (not(ignore_first) and count == 1) or (ignore_first and count == 2):
            return i
        i = i+1

    return 0

def get_file_name(num):
    cf = FileNames['Name'][num]
    m = re.search('(.+?).mp3', cf)
    if m:
        return m.group(1)
        return ''

def get_segment_time(string):
    st = 0
    et = 0
    m = re.search('stime="(.+?)"', string)
    if m:
        st = m.group(1)
    m = re.search('etime="(.+?)"', string)
    if m:
        et = m.group(1)
    return float(st), float(et)

def write_output_files(StartOfFileLoc, FileNum, FirstStringRemoveFlag):
    CurrentTxtFileName = 'Output_text/'+get_file_name(FileNum)
    CurrentInputAudioFileName = 'Input_audio/'+get_file_name(FileNum)+'.mp3'
    CurrentOutputAudioFileName = 'Output_audio/'+get_file_name(FileNum)
    EndOfFileLoc = find_next_endoffile (lines, StartOfFileLoc, FirstStringRemoveFlag)
    #Count number of segments and define general speech properties
    i = StartOfFileLoc
    NumSegments = 0
    while i <= EndOfFileLoc:
        k, i = get_speech_segment_range(lines, i)
        NumSegments = NumSegments + 1

    GeneralProperties = get_word(lines[EndOfFileLoc])

    LastSegmentLength = i-k

    if EndOfFileLoc == k+1:
        TrimSegment = True
    else:
        TrimSegment = False
    
    print ('Number of Segments: ', NumSegments)
    print ('General properties: ', GeneralProperties)

    if not(is_general_tag(GeneralProperties)) and not(is_noise_tag(GeneralProperties)):
        return

    CurLoc = StartOfFileLoc
    if NumSegments == 1:
        SegmentStart, SegmentEnd = get_speech_segment_range(lines, CurLoc) 
        CurText=''
        if FirstStringRemoveFlag:
            StartFrom = SegmentStart+2
        else:
            StartFrom = SegmentStart+1
        for i in range(StartFrom, SegmentEnd):
            CurText = CurText + get_word(lines[i])+' '
        TempTxtFileName = CurrentTxtFileName + '.txt'
        f = open(TempTxtFileName, 'w')
        f.write(CurText)
        f.close()
        TempAudioFileName = CurrentOutputAudioFileName + '.mp3'
        copyfile(CurrentInputAudioFileName, TempAudioFileName)
    elif NumSegments == 2 and TrimSegment:
        SegmentStart, SegmentEnd = get_speech_segment_range(lines, CurLoc) 
        CurText=''
        if FirstStringRemoveFlag:
            StartFrom = SegmentStart+2
        else:
            StartFrom = SegmentStart+1
        for i in range(StartFrom, SegmentEnd):
            CurText = CurText + get_word(lines[i])+' '
        TempTxtFileName = CurrentTxtFileName + '.txt'
        f = open(TempTxtFileName, 'w')
        f.write(CurText)
        f.close()
        TempAudioFileName = CurrentOutputAudioFileName + '.mp3'
        copyfile(CurrentInputAudioFileName, TempAudioFileName)
        CurLoc = SegmentEnd + 1
        SegmentStart, SegmentEnd = get_speech_segment_range(lines, CurLoc) 
    else:
        CurSeg = 1
        AllDuration = 0
        OldEndTime = 0
        Sound = AudioSegment.from_mp3(CurrentInputAudioFileName)
        while CurSeg <= NumSegments-1:
            SegmentStart, SegmentEnd = get_speech_segment_range(lines, CurLoc) 
            CurText=''
            if (CurSeg == 1) and FirstStringRemoveFlag:
                StartFrom = SegmentStart+2
            else:
                StartFrom = SegmentStart+1
            for i in range(StartFrom, SegmentEnd):
                CurText = CurText + get_word(lines[i])+' '
            CurText = CurText + '   '+GeneralProperties
            TempTxtFileName = CurrentTxtFileName + '(' + str(CurSeg) + ').txt'
            f = open(TempTxtFileName, 'w')
            f.write(CurText)
            f.close()

            print(lines[SegmentStart])
            StartTime, EndTime = get_segment_time(lines[SegmentStart])
            Duration = EndTime-StartTime
            if CurSeg == 1:
                GapDuration = 0
            else:
                GapDuration = StartTime-OldEndTime
            AllDuration = AllDuration + GapDuration
            print(AllDuration, GapDuration, StartTime, EndTime, Duration)
            SegmentSound = Sound[1000*AllDuration:1000*(AllDuration + Duration)]
            TempOutputFileName = CurrentOutputAudioFileName + '(' + str(CurSeg) + ').mp3'
            SegmentSound.export(TempOutputFileName, format="mp3")
            AllDuration = AllDuration + Duration
            OldEndTime = EndTime

            

            CurLoc = SegmentEnd + 1
            CurSeg = CurSeg + 1
            SegmentStart, SegmentEnd = get_speech_segment_range(lines, CurLoc) 


    if (NumSegments > 1) and (LastSegmentLength > 2):
        NextString = SegmentStart
        NextFirstStringRemoveFlag = True
    else:
        NextString = SegmentEnd + 1       
        NextFirstStringRemoveFlag = False
        
    return NextString, NextFirstStringRemoveFlag


#Loading input data
FileNames = pd.read_csv('FileNames.csv')
text_file = open("takenotetyping_1458665071037.xml", "r")

lines = text_file.readlines()
text_file.close()

#Locate content
StartContentLine = find_segment_list_begin(lines)
EndContentLine = find_segment_list_end(lines)

StartOfFileLoc = StartContentLine+1
CurFileNum = 0
CurStringRemoveFlag = False

while (StartOfFileLoc < EndContentLine):
    print ('Proceed with line # ', StartOfFileLoc)
    print ('File number ', CurFileNum)
    StartOfFileLoc, CurStringRemoveFlag = write_output_files(StartOfFileLoc, CurFileNum, CurStringRemoveFlag)
    CurFileNum = CurFileNum + 1
    print('')
