# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 15:12:37 2016


"""
import os
from pydub import AudioSegment,silence
from pydub.utils import mediainfo
import xml.sax
import pandas as pd 
from shutil import copyfile
os.chdir(os.path.dirname(os.path.realpath(__file__)))

class Common():
     def __init__(self):
         
         self.logFile="parser.log"
         self.audioInDir = 'Input_audio'
         self.txtOutDir = 'Output_text'
         self.audioOutDir = 'Output_audio'
         self.noiseOutDir = 'Output_noise'
         if not   os.path.exists(self.audioInDir):
            raise Exception('Audio input directory not found')
         
         self.fileNamesList=pd.read_csv('FileNames.csv')['Name'] 
            
         
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
         self.result=[]
         

     def findSilence(self,segment):    
         silenceSegmentsList = silence.detect_silence(segment, min_silence_len=self.minSilenceLen, silence_thresh=self.silenceThresh)
         if len(silenceSegmentsList)==0:
             self.log('not found silence segments with min_silence_len={0} and silence_thresh={1}'.format(self.minSilenceLen,self.silenceThresh))
             return 0
         return   (silenceSegmentsList[-1][0]+silenceSegmentsList[-1][1])//2  
         
     def writeFilePart(self, inFile, count, soundToWrite, original_bitrate, from_,to_):
         TempOutputFileName = '{0}({1})_{2}_{3}.mp3'.format(self.getFileName(inFile),count,from_,to_)
         soundToWrite.export(os.path.join(self.audioOutDir,TempOutputFileName), format="mp3", bitrate=original_bitrate)
         self.log('    write file "{0}"'.format(TempOutputFileName))
         self.result.append({'file':TempOutputFileName, 'from':from_,'to':to_,'text':''})
         
     def cut(self,inFile):
         self.result[:]=[]
         self.log('Begin work with file '+ inFile)
         inFile = os.path.join(self.audioInDir,inFile)
         sound = AudioSegment.from_mp3(inFile)
         original_bitrate = mediainfo(inFile)['bit_rate']
         soundLen = len(sound)         
         if soundLen < self.minSoundLen:
             self.log("   sound is less then {0} msec".format(self.minSoundLen))
             return []
         if soundLen < self.maxTime:
             self.log("   sound  is less then {0} msec".format(self.maxTime))
             return [] 

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
             self.writeFilePart(inFile, count, soundToWrite, original_bitrate, begin, cut)
             
             begin = cut+1
             count+=1
             timeLeft = soundLen-(cut+1)             
        
         self.writeFilePart(inFile, count, sound[cut+1:soundLen], original_bitrate, cut+1,soundLen)
         self.log('    cut OK')
         return self.result    

class parserHandler(xml.sax.ContentHandler, Common):
    def __init__(self, Cut):
         Common.__init__(self)
         self.words = []
         self._cut=Cut
         self._countFiles = 0
         self._countMs = 0
         self.generalTagList = [
            'female/native', 
            'male/native', 
            'male/non-native',
            'female/non-native', 
            'female/foreign–language',
            'male/foreign–language'        
         ]
         self.noiseTagList = [
            'bad-audio',
            'no-relevant-speech'
         ]
         self.endTagDivider = "  "
         
    def checkWordsFromList(self, content='', list_=[]):
        return any(word in content for word in list_)
         
    def startElement(self, name, attrs):
        self._curentTag=name
        if self._curentTag == "Word":
            self._currentStime=float(attrs.get("stime"))*1000
            self._currentDur=float(attrs.get("dur"))*1000
        
    #def endElement(self,name): 
    def _copyToNoise(self):
        fileName=self._currentMp3()
        copyfile(os.path.join(self.audioInDir, fileName), os.path.join(self.noiseOutDir,fileName))  
        
    def characters(self, content):
        if self._curentTag == "Word":
            if self.checkWordsFromList(content, self.generalTagList):
                if  self.words:
                    self.words[-1]['word']+= self.endTagDivider + content
                else:
                    self.log('    Empty file!')
                    
                self.onFileEnd()
                return
            if self.checkWordsFromList(content, self.noiseTagList): 
                self.onFileEnd(True)
                return
            if content.rstrip()!='':
                self.words.append({'word':content.rstrip(), 'stime':self._currentStime,'dur':self._currentDur})
    
    def onFileEnd(self, noise=False):
        if self.words:        
            self.log('    data for recording a text file has been read from xml from stime={0} to (include) stime={1} '.format(self.words[0]['stime'],self.words[-1]['stime']))
        else:
             self.log('    No words in file!!!')
        
        if noise:
            self._copyToNoise()
        else:
            cutRes = self._cut.cut(self._currentMp3())            
            if cutRes:
                to=0                
                for res in cutRes:
                    self.log('     --------')
                    self.log('    Res before='+str(res))                    
                    from_=res['from']+ self._countMs
                    to=res['to']+ self._countMs #TODO в файле сквозное время, надо накапливать 
                    self.log('     from={0};to={1};_countMs={2};'.format(from_,to,self._countMs))
                    for word in self.words:                        
                        if word['stime']>=from_ and word['stime']<to:
                            res['text']+=word['word'] #TODO неоптимально (лишние проходы по words) 
                            #self.log('     '+str(word))    
                            #self.words.remove(word)
                        #else:
                            #break
                    self.log('    Res after='+str(res))                            
                    f = open(os.path.join(self.txtOutDir,self.trimExt(res['file'])+'.txt'), 'w')
                    f.write(res['text'])
                    f.close()
                self._countMs +=  to 
            else:
                print()
                #
                
        self._countFiles+=1     
        self.words[:]=[]
        
    def _currentMp3(self):
        return self.fileNamesList[self._countFiles]    
        
        
def main():
   
    
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    c = CutMp3()
    parseHandler = parserHandler(c)
    parser.setContentHandler(parseHandler)
    parser.parse("takenotetyping_1458665071037.xml")
   
    #cutMp3(inFile, outDir)
   
    
   
    
main()    
        