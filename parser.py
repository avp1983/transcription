import xml.sax 
import pandas as pd
import os




class parserSAXHandler(xml.sax.ContentHandler):
    def __init__(self, fileNamesList=[]):
        self._fileNamesList = fileNamesList        
        self._countFiles = 0
        self._parentFlag = False
        
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

    def startElement(self, name, attrs):
        self._curentTag=name
        if name == "SpeechSegment":
           self._parentFlag = True
           self._countChilds=0
           self._text=''
        elif self._parentFlag:
           self._countChilds+=1 
           #self._childlist.append(name)

    def endElement(self,name):
        if name == "SpeechSegment":
            self._parentFlag = False
    
    def characters(self, content):
        if self._curentTag == "Word": 
            if self._checkWordsFromList(content, self.generalTagList):
                 self._text += self.endTagDivider + content
                 self._writeTxt();
                 self._countFiles+=1
                
                
                
            self._text += content
            
    def _trimExt(self, fileName=''):
        return    os.path.splitext(fileName)[0]        
        
    def _writeTxt(self):
        TempTxtFileName = self.txtOutDir +self._trimExt(self._fileNamesList[self._countFiles]) + '.txt'
        f = open(TempTxtFileName, 'w')
        f.write(self._text)
        f.close()
    
    def _checkWordsFromList(self, content='', list_=[]):
        return any(word in content for word in list_)

        

def main():
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    fileNames = pd.read_csv('FileNames.csv')
    parseHandler = parserSAXHandler(fileNames['Name'])
    parser.setContentHandler(parseHandler)
    parser.parse("ideal.xml")





if ( __name__ == "__main__"):
    main()