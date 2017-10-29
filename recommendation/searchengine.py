from urllib import request
from urllib import parse
from bs4 import BeautifulSoup
import sqlite3 as sqlite
import options
import os
import re

ignoredwords=['a', 'new', 'some', 'more', 'my', 'own', 'the', 'many', 'other', 'another']

class crawler:
    def __init__ (self, dbname):
        dbname=os.path.join(options.FLAGS.input_dir,dbname)
        self._conn = sqlite.connect(dbname)


    def __del__ (self):
        self._conn.close()


    def dbcommit(self):
        self._conn.commit()


    def execute(self, query):
        try:
            c = self._conn.cursor()
            return c.execute(query)
        except sqlite.Error as e:
            print(e)
            raise e


    def create_index_tables(self):
        self.execute('create table urllist(url text)')
        self.execute('create table wordlist(word text)')
        self.execute('create table wordlocation(urlid integer,wordid integer,location integer)')
        self.execute('create table link(fromid integer, toid integer)')
        self.execute('create table linkwords(wordid integer,linkid integer)')
        self.execute('create index wordidx on wordlist(word)')
        self.execute('create index urlidx on urllist(url)')
        self.execute('create index wordurlidx on wordlocation(wordid)')
        self.execute('create index urltoidx on link(toid)')
        self.execute('create index urlfromidx on link(fromid)')
        self.dbcommit()


    def add_to_index(self, url, soup):
        if self.is_indexed(url):
            return
        print('Indexing %s' % url)
        text=self.get_text_only(soup)
        words=self.separate_words(text)
        urlid=self.get_entry_id('urllist', 'url', url)
        for i in range(len(words)):
            word = words[i]
            if word in ignoredwords:
                continue
            wordid=self.get_entry_id('wordlist', 'word', word)
            self.execute('insert into wordlocation(urlid,wordid,location) values({},{},{})'.format(urlid,wordid,i))


    def get_entry_id(self,table,field,value,createnew=True):
        cur=self.execute("select rowid from {} where {}='{}'".format(table, field, value))
        res=cur.fetchone()
        if res is None:
            cur=self.execute("insert into {}({}) values('{}')".format(table, field, value))
            return cur.lastrowid
        else:
            return res[0]


    def get_text_only(self, soup):
        v=soup.string
        if v is None:
            c=soup.contents
            resulttext=''
            for t in c:
                subtext=self.get_text_only(t)
                resulttext+=subtext+'\n'
            return resulttext
        else:
            return v.strip()


    def separate_words(self, text):
        return [s.lower() for s in re.split(pattern=r'\W*', string=text) if s != '']


    def is_indexed(self, url):
        u=self.execute("select rowid from urllist where url='{}'".format(url)).fetchone()
        if u is not None:
            v=self.execute("select * from wordlocation where urlid={}".format(u[0])).fetchone()
            if v is not None:
                return True
        return False


    def add_link_ref(self, url_from, url_to, link_text):
        words=self.separate_words(link_text)
        fromid=self.get_entry_id('urllist', 'url', url_from)
        toid=self.get_entry_id('urllist', 'url', url_to)
        if fromid == toid:
            return
        cur=self.execute("insert into link(fromid,toid) values({},{})".format(fromid,toid))
        linkid=cur.lastrowid
        for word in words:
            if word in ignoredwords:
                continue
            wordid=self.get_entry_id('wordlist', 'word', word)
            self.execute("insert into linkwords(linkid,wordid) values({},{})".format(linkid,wordid))


    def crawl(self, pages, depth=2):
        for i in range(depth):
            newpages=set()
            for page in pages:
                try:
                    c=request.urlopen(page)
                except:
                    print('couldnot open {}'.format(page))
                    continue
                soup=BeautifulSoup(c.read(), 'html5lib')
                self.add_to_index(page, soup)

                links=soup('a')
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = parse.urljoin(page, link['href'])
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0]
                        if url[0:4]=='http' and not self.is_indexed(url):
                            newpages.add(url)
                        link_text = self.get_text_only(link)
                        self.add_link_ref(page, url, link_text)
                self.dbcommit()
            pages=newpages


class searcher:
    def __init__ (self, dbname):
        dbname=os.path.join(options.FLAGS.input_dir, dbname)
        self._conn=sqlite.connect(dbname)


    def __del__ (self):
        self._conn.close()


    def execute(self, query):
        try:
            c = self._conn.cursor()
            return c.execute(query)
        except sqlite.Error as e:
            print(e)
            raise e


    def get_match_rows(self, q):
        fieldlist='w0.urlid'
        tablelist=''
        clauselist=''
        wordids=[]
        words=q.split(' ')
        tablenumber=0

        for word in words:
            wordrow=self.execute("select rowid from wordlist where word='{}'".format(word)).fetchone()
            if wordrow is not None:
                wordid=wordrow[0]
                wordids.append(wordid)
                if tablenumber>0:
                    tablelist+=','
                    clauselist+=' and '
                    clauselist+='w{}.urlid=w{}.urlid and '.format(tablenumber-1,tablenumber)
                fieldlist+=',w%d.location' % tablenumber
                tablelist+='wordlocation w%d' % tablenumber
                clauselist+='w%d.wordid=%d' % (tablenumber,wordid)
                tablenumber+=1

        fullquery='select {} from {} where {}'.format(fieldlist,tablelist,clauselist)
        cur=self.execute(fullquery)
        rows=[row for row in cur]
        return rows,wordids