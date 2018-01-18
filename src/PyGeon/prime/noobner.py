from nltk import word_tokenize
import operator
import json

CITIES = set([str(i.lower()) for i in json.loads(open("../../../TDS/Spiders/cities.json", 'r').read()).keys()])
CATMAP = {
    'devmeets':
    {
        'dev',
        'dev-meet',
        'dev-meetup',
        'developer',
        'developer-meet',
        'developer-meetup',
        'meet',
        'meets',
        'meetup',
        'meetups'},
    'hackathons':
    {
        'development',
        'hack',
        'hackathon',
        'hackathons',
        'hacks',
        'pitch',
        'product',
        'startup'},
    'techfests':
    {
        'fest',
        'symposium',
        'tech',
        'tech-fest',
        'techfest',
        'techfests',
        'techno',
        'technology-fest'
    }
}

#print CITIES
#print CATMAP

def getCity(sentence):
    sentset = set(word_tokenize(sentence.lower()))
    #print sentset
    #print CITIES
    #print sentset.intersection(CITIES)
    return list(sentset.intersection(CITIES))

def getCat(sentence):
    sentset = set(word_tokenize(sentence.lower()))
    #print sentset
    d = {}
    for i in CATMAP.items():
        d[i[0]] = len(sentset.intersection(i[1]))
    #print d
    return max(d.iteritems(), key=operator.itemgetter(1))[0]

def shadyNER(sentence):
    return (getCity(sentence), getCat(sentence))
