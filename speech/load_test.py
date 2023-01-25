import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import speech_recognition as sr
from nltk.tag import HunposTagger


# def speech_label():
#     adj=[]
#     noun=[]
#     r = sr.Recognizer()
#     mic = sr.Microphone()
#     stops = stopwords.words('english')
#     home=os.path.abspath(os.getcwd())
#     model=home+'\Hunpos\english.model'
#     binary=home+'\Hunpos\hunpos-tag.exe'
#     label=""
#     print("Please give fetch your command!")
#     while True:
#         try:
#             with mic as source:
#                 print("Listening...")
#                 r.adjust_for_ambient_noise(source)
#                 # audio = r.record(source=mic, duration=10)
#                 audio = r.listen(source)
#         except:
#                 continue
#         userSpeech=r.recognize_google(audio)
#         print(userSpeech)
#         tokens = word_tokenize(userSpeech)
#         ht = HunposTagger(model,binary)
#         tagged=ht.tag(tokens)
#         # remove stop words
#         tagged = [t for t in tagged if not t[0] in stops]
#         #extract adjectives and nouns
#         for t in tagged:
#             if t[1] == b'JJ':
#                 adj.append(t[0])
#             if t[1] == b'NN':
#                 noun.append(t[0])
#         label=(' '.join(adj) + " " + ' '.join(noun)).strip()
#         if label!="":
#             return label


if __name__=="__main__":
    home=os.path.abspath(os.getcwd())
    model = os.path.join(home, 'Hunpos', 'english.model')
    binary = os.path.join(home, 'Hunpos', 'hunpos-tag')
    ht = HunposTagger(model,binary)
    print(home)
    print(model)
    print(binary)
