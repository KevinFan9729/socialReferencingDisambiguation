import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
import speech_recognition as sr
from nltk.tag import HunposTagger

adj=[]
noun=[]
#pip install nltk==3.4.5 for python 2.7

r = sr.Recognizer()
mic = sr.Microphone()

userSpeech=""

# with mic as source:
#     r.adjust_for_ambient_noise(source)
#     audio = r.listen(source)
# userSpeech=r.recognize_google(audio)
# #     # user_speech=r.recognize_sphinx(audio)#pip install pocketsphinx

# userSpeech="could you please pass me the salt container"
# userSpeech="could you pass me the salt container please"
# userSpeech="pass me the big salt container please"
userSpeech="hand me big salt container please"
# userSpeech="The quick brown fox jumps over the lazy dog"

model="C:/Users/kevei/Documents/english.model"
binary="C:/Users/kevei/Documents/hunpos-tag.exe"
print(userSpeech)
tokens = word_tokenize(userSpeech)
ht = HunposTagger(model,binary)
tagged=ht.tag(tokens)
print(tagged)

stops = stopwords.words('english')

tagged = [t for t in tagged if not t[0] in stops]
print(tagged)
for t in tagged:
    if t[1] == b'JJ':
        adj.append(t[0])
    if t[1] == b'NN':
        noun.append(t[0])
label=(' '.join(adj) + " " + ' '.join(noun)).strip()

print(label)
# print(userSpeech)
# print(tokens)



# stemmer = PorterStemmer()
# stemmed = [stemmer.stem(word) for word in tokens]

# # print(stemmed)


# #print(tagged)