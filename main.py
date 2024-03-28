from flask import Flask, render_template, request
from indexer import indexer
import time


app = Flask(__name__)

global page
global keys
dataset = indexer()
def init():
    print('start up')


@app.route('/')
def main():
    init()
    return render_template('search.html', error=True)


@app.route('/search/', methods=['POST'])
def search():

        global keys
        global checked
        global querys

        keys = request.form['key_word']
        selected = request.form['order']
        checked = ['checked="true"', '']
        # print(selected)
        for i in range(2):
            if i == int(selected):
                checked[i] = 'checked="true"'
            else:
                checked[i] = ''
        # print(checked)
        print(keys)
        if keys not in ['']:
            print(time.clock())
            flag,page,querys = searchidlist(keys,selected)
            print(flag)
            print('flag')
            if flag==0:
                return render_template('search.html', error=False)
            docs = cut_page(page, 0,querys)
            print(time.clock())
            return render_template('high_search.html', checked=checked, key=keys, docs=docs, page=page,querys=querys,
                                   error=True)
        else:
            return render_template('search.html', error=False)




def searchidlist(key, selected=0):
    global page
    global doc_id
    flag, doc_id,querys = dataset.getresult(key,int(selected))
    page = []
    for i in range(1, (len(doc_id) // 10 + 2)):
        page.append(i)
    return flag,page,querys



def cut_page(page, no,query=[]):
    docs = getall(doc_id[no*10:page[no]*10],query)
    return docs



def find(docid):
    # print(docid)
    title=dataset.gettitle(docid)
    # print(title)
    url=dataset.geturl(docid)
    title = dataset.gettitle(docid)
    body = dataset.gettext(docid)
    time = dataset.gettime(docid)
    thumbnail=dataset.getthumbnail(docid)
    meta_tag=dataset.getmeta_tags(docid)

    doc = {'image': thumbnail, 'title': title,'url':url,
           'meta_tag': meta_tag, 'time': time,'body': body,
           'id': docid, 'extra': []}
    print(doc)

    return doc
def snip(text,keys):
    print('sniping.....')
    res=""
    for key in keys:
        if text.__contains__(key):
            fromi = text.index(key) - 100
            if fromi<0:fromi=0
            toi = text.index(key) + 150
            # print(fromi)
            # print(toi)
            # print(text[fromi:toi])
            res+="..."+ text[fromi:toi]+""
    return res

def getall(ids,query=[]):
    docs = []
    for docid in ids:
        title = dataset.gettitle(docid)
        # print(title)
        url = dataset.geturl(docid)
        title = dataset.gettitle(docid)
        summary = snip(dataset.gettext(docid),query)
        # if summary.__len__()>300:
        #     summary=dataset.getsummary(docid)
        time = dataset.gettime(docid)
        thumbnail = dataset.getthumbnail(docid)
        meta_tag = dataset.getmeta_tags(docid)
        doc = {'image': thumbnail, 'title': title, 'url': url,
               'meta_tag': meta_tag, 'time': time, 'summary': summary,
               'id': docid, 'extra': []}
        docs.append(doc)
    return docs
@app.route('/search/page/<page_no>/', methods=['GET'])
def next_page(page_no):
    try:
        page_no = int(page_no)
        docs = cut_page(page, (page_no-1),querys)
        return render_template('high_search.html', checked=checked, key=keys, docs=docs, page=page,querys=querys,
                               error=True)
    except:
        print('next error')



@app.route('/search/<id>/', methods=['GET', 'POST'])
def content(id):
    try:
        doc = find(int(id))
        return render_template('content.html', doc=doc)
    except:
        print('content error')



if __name__ == '__main__':
    app.run()
