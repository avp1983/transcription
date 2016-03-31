# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 19:21:48 2016

@author: 
"""

import speech_recognition as sr

# obtain path to "english.wav" in the same folder as this script
from os import path
WAV_FILE = path.join(path.dirname(path.realpath(__file__)), "0a94.wav")

# use "english.wav" as the audio source
r = sr.Recognizer()
with sr.WavFile(WAV_FILE) as source:
    audio = r.record(source) # read the entire WAV file

# recognize speech using Sphinx
try:
    print("Sphinx thinks you said " + r.recognize_sphinx(audio))
except sr.UnknownValueError:
    print("Sphinx could not understand audio")
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))