import heapq
import io, json
from builtins import print
from collections import OrderedDict
from normalization import Normalizers
from tockenization import Tockenizer
import math
from hazm import *
from pandas import read_excel
from bs4 import BeautifulSoup
import html2text
from datetime import datetime
import util

nr = Normalizers()
tc = Tockenizer()

class indexer:

    def __init__(self):
        self.createindex()
        print('init indexer')

    index = {}
    listC = [['', 0]]
    df_total= None
    normalizer = Normalizer()
    # stemmer = Stemmer()
    lemmatizer = Lemmatizer()
    df = None
    stopwords = ['از', 'به', 'برای', 'که', 'در']

    def buildIndex(self, text, docName, docTime):
        text = self.normalizer.normalize(text)
        text = util.clean_sentence(text)
        words = text.split()
        for i in range(0, len(words)):
            w1 = words[i]
            w2= nr.cleanup(w1)
            w3= tc.tockenize_steming_hamsansaz(w2)
            if len(w3)>0:
                w4=w3[0]
                w4= w4.replace(' ', '')
                print('*******')
                print("\""+ w4+ "\"")
                self.addtoindex(w4, docName, text.count(w1), docTime, i)
            else:
                self.addtoindex(w1, docName, text.count(w1), docTime, i)
    def addtoindex(self, word, docName, occursion, time, position):
        if word not in self.index.keys():
            self.index[word] = {}
        if docName not in self.index[word].keys():
            self.index[word][docName] = {}
        if position not in self.index[word][docName].keys():
            self.index[word][docName][position] = []
        self.index[word][docName][position].append([occursion, time])
        # self.index[word].sort()
        # for l in index[word]:

    def quotIntersection(self, quoted):
        result = []
        counters = []
        splited = quoted.split(" ")
        if splited[0] in self.index:
            docsWithSplited = self.index[splited[0]].keys()
            for i in splited:
                if i in self.index:
                    docsWithSplited = self.intersection(docsWithSplited, self.index[i].keys())
                else:
                    docsWithSplited = []
            for i in docsWithSplited:
                counter = 0
                for j in self.index[splited[0]][i].keys():
                    flag = True
                    for k in range(0, len(splited)):
                        if (j + k) not in self.index[splited[k]][i].keys():
                            flag = False
                    if flag is True:
                        counter = counter + 1
                if counter > 0 and i not in result:
                    result.append(i)
                    counters.append(counter)
        else:
            result = []
            counters = []
        return result,counters

    def sort(self , docList , termList , type):
        print(type)
        res = []
        if type == 0:
            print('sort by relevent')
            docList = sorted(
                docList,
                key=lambda x: x[1], reverse=True
            )
        else:
            if type == 1:
                print('sort by time')
                docList = sorted(
                    docList,
                    key=lambda x: datetime.strptime(x[2].replace('nd', 'th').replace('rd', 'th').replace('1st', '1th'), '%B %dth %Y, %H:%M:%S.000'), reverse=True
                )
            else:
                print("sort by tf-idf")
                myHeap = []
                queryVect = []
                docVectS = []
                vectsRowS = []

                heapq.heapify(myHeap)

                # calculating the tf-idf
                for i in termList:
                    # term without quot
                    if len(i.split())==1:
                        if i in self.index:
                            termPostings = self.index[i]
                            docFreq = len(termPostings)
                            print("termList.count(i): in if")
                            print(termList.count(i))
                            queryVect.append((1 + math.log(termList.count(i))) * math.log(10000 / (docFreq + 1) ))
                            aRowOfVectS = []
                            for j in docList:
                                if j[0] in termPostings.keys():
                                    termFreq = len( termPostings[ j[0] ] )
                                    tf_idf = (1 + math.log(termFreq)) * math.log(10000 / (docFreq + 1))
                                else:
                                    tf_idf = 0
                                print( termFreq )

                                aRowOfVectS.append(tf_idf)
                        else:
                            aRowOfVectS = []
                            queryVect.append(0)
                            for j in docList:
                                aRowOfVectS.append(0)
                        vectsRowS.append(aRowOfVectS)
                    else:
                        print(i)
                        theDocs , termFreqS = self.quotIntersection(i)
                        docFreq = len(theDocs)
                        print(termList)
                        print("termList.count(i): in else" )
                        print(termList.count(i))
                        queryVect.append(( 1 + math.log(termList.count(i)) ) * math.log(10000 / (docFreq + 1) ))
                        aRowOfVectS = []
                        for j in docList:
                            if j[0] in theDocs:
                                termFreq = termFreqS [ theDocs.index( j[0] ) ]
                                tf_idf = (1 + math.log(termFreq )) * math.log(10000 / (docFreq+1) )
                                aRowOfVectS.append(tf_idf)
                            else:
                                aRowOfVectS.append(0)
                        vectsRowS.append(aRowOfVectS)

                # making the doc vectors
                for i in range( 0 , len(vectsRowS[0]) ):
                    aDocVect = []
                    for j in range ( 0 , len(vectsRowS) ):
                        aDocVect.append(vectsRowS[j][i])
                    docVectS.append(aDocVect)

                # calculating the similarities and storing them in a heap :)
                for i in range( 0 , len(docVectS) ):
                    theDocVec = docVectS[i]
                    makhraj1 = 0
                    makhraj2 = 0
                    surat = 0
                    for j in range(0 , len(theDocVec) ):
                        print("theDocVec")
                        print(theDocVec)
                        print("queryVect")
                        print(queryVect)
                        surat = theDocVec[j] * queryVect[j] + surat
                        makhraj1 = theDocVec[j] * theDocVec[j] + makhraj1
                        makhraj2 = queryVect[j] * queryVect[j] + makhraj2
                    heapq.heappush(myHeap, (surat/makhraj1*makhraj2,) + (docList[i]))
            docList = heapq.nlargest(50 , myHeap)

        for item in docList:
            # print(item[0])
            if not res.__contains__(item[1]):
                res.append(item[1])
        return res

    def save(self):
        global index
        indexFile = open("biword-index.json", "w")
        index = OrderedDict(sorted(index.items(), key=lambda t: t[0]))
        indexFile.write(json.dumps(index))
        indexFile.close()
        print("finish wrting index file")

    def Tokenize(self, Query):
        print(Query)
        Query= Query.replace('.', ' ')
        print(Query)
        Sentinel= True
        Quote_List_Positive= []
        Quote_List_Negative= []
        Token_List_Positive = []
        Token_List_Negative = []
        while Sentinel:
            start_pt = Query.find("\"")
            end_pt = Query.find("\"", start_pt + 1)  # add one to skip the opening "
            if start_pt != -1 and end_pt != -1:
                Query_Length= len(Query)
                if Query[start_pt-1:start_pt]=='!':
                    Quote = Query[start_pt + 1: end_pt]
                    Query = Query[0:start_pt-1] + Query[end_pt + 1: Query_Length]
                    if Quote != "":
                        Quote_List_Negative.append(Quote)
                else :
                    Quote = Query[start_pt + 1: end_pt]
                    Query = Query[0:start_pt] + Query[end_pt + 1: Query_Length]
                    if Quote!= "":
                        Quote_List_Positive.append(Quote)
            else :
                Sentinel= False

        Query_Tokenize= Query.split(" ");
        for Temporary_X in range(len(Query_Tokenize)):
            if Query_Tokenize[Temporary_X][:1]=='!':
                if Query_Tokenize[Temporary_X] != "":
                    Token_List_Negative.append(Query_Tokenize[Temporary_X][1:])
            else:
                if Query_Tokenize[Temporary_X] != "":
                    Token_List_Positive.append(Query_Tokenize[Temporary_X][0:])
        for Temporary_1 in range (0, len(Quote_List_Positive)):
            X_1= Quote_List_Positive[Temporary_1]
            w2 = nr.cleanup(X_1)
            w3 = tc.tockenize_steming_hamsansaz(w2)
            if len(w3) > 0:
                w_x= w3[0]
                w_x_1 = w_x.split(' ')
                w_x_2 = ""
                for Temporary_2 in range(0, len(w_x_1)):
                    if w_x_1[Temporary_2]!= "" and w_x_2!= "":
                        w_x_2= w_x_2+ ' '+ w_x_1[Temporary_2]
                    elif w_x_1[Temporary_2]!= "" and w_x_2== "":
                        w_x_2= w_x_1[Temporary_2]
                Quote_List_Positive[Temporary_1]= w_x_2
        for Temporary_1 in range(0, len(Quote_List_Negative)):
            X_2 = Quote_List_Negative[Temporary_1]
            w4 = nr.cleanup(X_2)
            w5 = tc.tockenize_steming_hamsansaz(w4)
            if len(w5) > 0:
                w_x = w5[0]
                w_x_1 = w_x.split(' ')
                w_x_2= ""
                for Temporary_2 in range(0, len(w_x_1)):
                    if w_x_1[Temporary_2]!= "" and w_x_2!= "":
                        w_x_2= w_x_2+ ' '+ w_x_1[Temporary_2]
                    elif w_x_1[Temporary_2]!= "" and w_x_2== "":
                        w_x_2= w_x_1[Temporary_2]
                Quote_List_Negative[Temporary_1] = w_x_2
        for Temporary_1 in range(0, len(Token_List_Positive)):
            X_3 = Token_List_Positive[Temporary_1]
            w6 = nr.cleanup(X_3)
            w7 = tc.tockenize_steming_hamsansaz(w6)
            if len(w7) > 0:
                w_x = w7[0]
                w7= w_x.replace(' ', '')
                Token_List_Positive[Temporary_1] = w7
        for Temporary_1 in range(0, len(Token_List_Negative)):
            X_4 = Token_List_Negative[Temporary_1]
            w8 = nr.cleanup(X_4)
            w9 = tc.tockenize_steming_hamsansaz(w8)
            if len(w9) > 0:
                w_x = w9[0]
                w9 = w_x.replace(' ', '')
                Token_List_Negative[Temporary_1] = w9

        return Quote_List_Positive, Quote_List_Negative, Token_List_Positive, Token_List_Negative

    def checkocc(self, list, query):
        for l in list:
            if l[0] == query:
                return True
        return False

    def intersection(self, lst1, lst2):
        lst3=[]
        for v in lst1:
            for v2 in lst2:
                if v==v2:
                    if v not in lst3:
                        lst3.append(v)

        return lst3

    def queryparser(self, query):
        print('start query parser')
        flag = False
        word = ""
        stack = []
        for char in query:
            if char == '"':
                if flag:
                    flag = False
                else:
                    flag = True
                if word.__len__() > 1:
                    stack.append(word.strip())
                word = ""
            if not flag and char == ' ' and word.__len__() > 1:
                stack.append(word.strip())
                word = ""
            if char != '"' and char != '.' and char != ':' and char != ',':
                word += char
        if word.__len__() > 1:
            stack.append(word.strip())
        print(stack)
        return stack

    def getresult(self, query, sorttype=2):
        query = util.clean_sentence(query)
        listr = []
        Quote_List_Positive, Quote_List_Negative, Token_List_Positive, Token_List_Negative= self.Tokenize(query)
        print('httttttth')
        print(Quote_List_Positive)
        print(Quote_List_Negative)
        print(Token_List_Positive)
        print(Token_List_Negative)
        if len(Token_List_Positive)!= 0:
            if Token_List_Positive[0] in self.index:
                listr= list( self.index[Token_List_Positive[0]] )
                for Temporary_1 in Token_List_Positive:
                    if Temporary_1 in self.index:
                          listr= self.intersection(listr, self.index[Temporary_1].keys())
            else:
                listr = []

        listr_1 = []
        for Temporary_1 in Quote_List_Positive:
            listr_1 , counters = self.quotIntersection(Temporary_1)
        print("listr1111")
        print("روابط عمومی"=="روابط عمومی")
        print(listr_1)
        print("listr")
        print(listr)
        if len(listr_1) != 0:
            if len(listr)!= 0:
                listr= self.intersection(listr, listr_1)
            else:
                listr = listr_1

        for Temporary_1 in Token_List_Negative:
            if Temporary_1 in self.index:
                for Temporary_2 in self.index[Temporary_1].keys():
                    if Temporary_2 in listr:
                        listr.remove(Temporary_2)

        listQuotNeg = []
        for Temporary_1 in Quote_List_Negative:
            listQuotNeg , counters = self.quotIntersection(Temporary_1)
            for i in listQuotNeg:
                listr.remove(i)

        listr_t= []
        for Temporary_1 in listr:
            docTime = self.df_total['publish_date'][Temporary_1]
            text = html2text.html2text(df['content'][Temporary_1])
            counter= 0
            for Temporary_2 in Token_List_Positive:
                counter= counter + text.count(Temporary_2)
            for Temporary_2 in Quote_List_Positive:
                counter= counter + text.count(Temporary_2)
            counter_total= len(Token_List_Positive) + len(Quote_List_Positive)
            listr_t.append( (Temporary_1, counter/counter_total, docTime) )
        query_list= Quote_List_Positive+ Token_List_Positive
        print("I am in result section:")
        print(listr)
        if len(listr) == 0:
            return 0, [], []
        else:
            return 1, self.sort(listr_t, query_list , 2), query_list

    def createindex(self):
        global df
        my_sheet = 'news'
        file_name = 'data.xlsx'  # name of your excel file
        df = read_excel(file_name, sheet_name=my_sheet)
        docID = 0
        self.df_total= df
        for i in range(0,100):
            text = html2text.html2text(df['content'][i])
            docTime = df['publish_date'][i]
            print(docID)
            print('===============================================')
            # print(text)
            self.buildIndex(text, docID, docTime)
            docID = docID + 1
            # if docID == 10: break
            # save()
        #self.heaps_law_computation()
        #self.zipf_law_computation()
        #self.champion_lists_computation(5)

    def heaps_law_computation(self):
        token_number = 0
        term_number = 0
        for temporary_1 in self.index.keys():
            if len(temporary_1.split()) == 1:
                term_number = term_number + 1
                token_number = token_number + len(self.index[temporary_1])
        print("\nHeaps' law: ")
        print("number of tokens: " + str(token_number))
        print("number of terms: " + str(term_number))
        print("prediction for number of terms: " + str(44 * (token_number ** 0.49)))

    def zipf_law_computation(self):
        print("\nZipf's law:")
        frequency_matrix = {}
        frequency_matrix_t = {}

        counter = 0
        maximum_number = 0
        maximum_word = ""
        for temporary_1 in self.index.keys():
            if len(temporary_1.split()) == 1:
                frequency_matrix[temporary_1] = len(self.index[temporary_1])
                frequency_matrix_t[temporary_1] = len(self.index[temporary_1])
                if maximum_number < len(self.index[temporary_1]):
                    maximum_number = len(self.index[temporary_1])
                    maximum_word = temporary_1
        print("1- word: " + maximum_word + ", absolute frequency: " + str(
            maximum_number) + ", relative frequency: 1" + ", expectation for relative frequency: 1")
        absolute_maximum_number = maximum_number
        absolute_maximum_word = maximum_word
        frequency_matrix[absolute_maximum_word] = -1
        frequency_matrix_t[absolute_maximum_word] = -1
        counter = 0
        for temporary_2 in frequency_matrix.keys():
            previous_number = 0
            previous_word = ""
            for temporary_3 in frequency_matrix.keys():
                if (previous_number <= frequency_matrix[temporary_3]) and (frequency_matrix_t[temporary_3] != -1):
                    previous_number = frequency_matrix[temporary_3]
                    previous_word = temporary_3
            maximum_number = previous_number
            maximum_word = previous_word
            frequency_matrix_t[maximum_word] = -1
            print(str(counter + 2) + "- word: " + maximum_word + ", absolute frequency: " + str(
                maximum_number) + ", relative frequency: " + str(
                maximum_number / absolute_maximum_number) + ", expectation for relative frequency: " + str(
                1 / (counter + 2)))
            counter = counter + 1

    def champion_lists_computation(self, parameter_1):
        champion_lists = {}
        index_secondary = self.index
        for temporary_1 in index_secondary.keys():
            if len(temporary_1.split()) == 1:
                print(temporary_1)
                for temporary_2 in range(0, parameter_1):
                    maximum_frequency = -0.5
                    maximum_document = -0.5
                    for temporary_2 in index_secondary[temporary_1].keys():
                        if maximum_frequency < len(index_secondary[temporary_1][temporary_2].keys()):
                            maximum_frequency = len(index_secondary[temporary_1][temporary_2].keys())
                            maximum_document = temporary_2
                    for temporary_2 in index_secondary[temporary_1].keys():
                        if temporary_2 == maximum_document:
                            if temporary_1 not in champion_lists.keys():
                                champion_lists[temporary_1] = {}
                            if temporary_2 not in champion_lists[temporary_1].keys():
                                champion_lists[temporary_1][temporary_2] = {}
                            champion_lists[temporary_1][temporary_2]= index_secondary[temporary_1][temporary_2]
                            index_secondary[temporary_1][temporary_2]= {}
        index_secondary = self.index
        for temporary_1 in index_secondary.keys():
            if len(temporary_1.split()) != 1:
                print(temporary_1)
                sentinel = True
                for temporary_2 in temporary_1.split():
                    if temporary_2 not in champion_lists.keys():
                        sentinel = False
                if sentinel == True:
                    champion_lists[temporary_1] = index_secondary[temporary_1]
        self.index = champion_lists

    def gettitle(self, itemindex):
        return df['title'][itemindex]

    def gettext(self, itemindex):

        soup = BeautifulSoup(str(df['content'][itemindex]), "html.parser")
        return soup.get_text()
        # return (html2text.html2text(str(df['content'][itemindex])))

    def gettime(self, itemindex):
        return df['publish_date'][itemindex]

    def getsummary(self, itemindex):
        return df['summary'][itemindex]

    def getmeta_tags(self, itemindex):
        return df['meta_tags'][itemindex]

    def getthumbnail(self, itemindex):
        return df['thumbnail'][itemindex]

    def geturl(self, itemindex):
        return df['url'][itemindex]

    def test(self):
        # print(df['title'][0])
        # query=  'ایران'
        query = 'ایران "حل مشکل" !تیم'
        # query='ایران "حل مشکل"'
        print('indexing finish')
        f, res, querys = self.getresult(query, 1)
        print(f)
        for r in res:
            print(r)
            print('title')
            print(self.gettitle(r))
            print('context')
            print(self.gettime(r))


if __name__ == '__main__':
    i = indexer()
    i.test()
