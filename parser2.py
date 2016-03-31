import xml.sax 
import pandas as pd
import os
from shutil import copyfile



class parserSAXHandler(xml.sax.ContentHandler):
    def __init__(self, fileNamesList=[]):
        self._fileNamesList = fileNamesList        
        self._countFiles = 0
        self._parentFlag = False
        self._textSegment = ''
        self._segmentCount = -1; 
        self._textList = []
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
        
        self.audioInDir = 'Input_audio/'
        self.txtOutDir = 'Output_text/'
        self.audioOutDir = 'Output_audio/'
        self.noiseOutDir = 'Output_noise/'
        if not   os.path.exists(self.audioInDir):
            raise Exception('Audio input directory not found')
        
        self._forceDir(self.txtOutDir,self.audioOutDir,self.noiseOutDir)
        
    def _forceDir(self, *dirs):
        for dir_ in dirs:
            if not os.path.exists(dir_):
                os.makedirs(dir_)

    def startElement(self, name, attrs):
        self._curentTag=name
        if name == "SpeechSegment":
           self._parentFlag = True
           self._textSegment = ''
           self._countChilds=0
           self._segmentCount += 1            
        elif self._parentFlag:
           self._countChilds+=1 
           #self._childlist.append(name)

    def endElement(self,name):
        if name == "SpeechSegment":
            self._parentFlag = False
            if self._textSegment !='':
                self._textList.append(self._textSegment)
    
    def characters(self, content):
        if self._curentTag == "Word": 
            if self._checkWordsFromList(content, self.generalTagList):
                 if len(self._textList)==0:
                     self._textList.append(self._textSegment)
                 
                 self._textList[-1] += self.endTagDivider + content                 
                 self._writeTxt();                 
                 self._textList[:] = []
                 self._countFiles+=1
                 self._segmentCount = -1
                 return
            if self._checkWordsFromList(content, self.noiseTagList): 
                 fileName =  self._currentMp3()                   
                 self._copyToNoise(fileName)
                 
                 self._textList[:] = []
                 self._countFiles+=1
                 self._segmentCount = -1
                 return
                
                 
                
            self._textSegment += content.rstrip()
            
    def _copyToNoise(self, fileName):
          copyfile(os.path.join(self.audioInDir, fileName), os.path.join(self.noiseOutDir,fileName))      
            
    def _trimExt(self, fileName=''):
        return    os.path.splitext(fileName)[0] 
        
    def _currentMp3(self):
        return self._fileNamesList[self._countFiles]
        
    def _currentFileWithoutExt(self):
        return self._trimExt(self._currentMp3())
        
    def _writeTxt(self):
        listCount =  len(self._textList)     
        if   listCount==1:      
            TempTxtFileName = os.path.join(self.txtOutDir, self._currentFileWithoutExt()+'.txt')
            f = open(TempTxtFileName, 'w')
            
         
                
            f.write(self._textList[0])
            f.close()
        elif listCount > 1:
           count=1
            
           for text in self._textList:
               #if listCount==count: break
               end = "({0}).txt".format(count)
               TempTxtFileName = os.path.join(self.txtOutDir, self._currentFileWithoutExt()+end)
               f = open(TempTxtFileName, 'w')
            
               f.write(text)
               f.close() 
               count +=1
        else:
            raise Exception('somthing is going wrong')    
            
    
    def _checkWordsFromList(self, content='', list_=[]):
        return any(word in content for word in list_)

        

def main():
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    fileNames = pd.read_csv('FileNames.csv')
    parseHandler = parserSAXHandler(fileNames['Name'])
    parser.setContentHandler(parseHandler)
    parser.parse("ideal2.xml")
    print("Finished")





if ( __name__ == "__main__"):
    main()