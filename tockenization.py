import re
from hazm import *
import hamsansaz
import steming
class Tockenizer:
    conjuctionphrase = [
        "مع ذلک", "علی ای حال", "بنا بر این", "چنان چه", "فیما بین", "چون که", "چندان که", "زیرا که", "همین که",
        "همان که", "چنان که",
        "تا اینکه", "از این رو", "از بس", "اکنون که", "از آنجا که", "از بس که", "اگر چه", "با این حال", "با وجود این",
        "به شرط آن که"
    ]

    conjunctionwithzwnj = [
        "مع‌ذلک", "علی‌ای‌حال", "بنا‌بر‌این", "چنان‌چه", "فیما‌بین", "چون‌که", "چندان‌که", "زیرا‌که", "همین‌که",
        "همان‌که", "چنان‌که",
        "تا‌اینکه", "از‌این‌رو", "از‌بس", "اکنون‌که", "از‌آنجا‌که", "از‌بس‌که", "اگر‌چه", "با‌این‌حال", "با‌وجود‌این",
        "به‌شرط‌آن‌که"
    ]
    tagger = POSTagger(model='resources/postagger.model')
    chunker = Chunker(model='resources/chunker.model')

    def tockenize_steming_hamsansaz(self,sent):
        for i in range(0,len(self.conjuctionphrase)):
            sent.replace(self.conjuctionphrase[i],self.conjunctionwithzwnj[i])

        tagged = self.tagger.tag(word_tokenize(sent))
        d=self.chunker.parse(tagged)
        # print(d)
        d=tree2brackets(self.chunker.parse(tagged))
        # print(d)
        interm = re.findall(r'\[([^]]*)]', d)
        res=[]
        for trm in interm:
            term=''
            isnaun = True
            if trm.split(" ")[0].startswith("V") :isnaun=False
            for i in range(len(trm.split(" "))-1):
                term+=(trm.split(" ")[i])+" "
            term=hamsansaz.hamsansazi(term)
            term=steming.stemming(term,isnaun)
            res.append(term)
        return res
