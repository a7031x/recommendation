import sqlite3 as sqlite
import os
import options
from math import tanh

class searchnet:
    def __init__(self,dbname):
        dbname=os.path.join(options.FLAGS.input_dir,dbname)
        self._conn=sqlite.connect(dbname)


    def __del__(self):
        self._conn.close()


    def execute(self, query):
        try:
            c = self._conn.cursor()
            return c.execute(query)
        except sqlite.Error as e:
            print(e)
            raise e


    def maketables(self):
        self.execute('create table hiddennode(create_key)')
        self.execute('create table wordhidden(fromid,toid,strength)')
        self.execute('create table hiddenurl(fromid,toid,strength)')
        self._conn.commit()


    def getstrength(self,fromid,toid,layer):
        if layer==0:
            table='wordhidden'
        else:
            table='hiddenurl'
        res=self.execute('select strength from {} where fromid={} and toid={}'.format(table,fromid,toid)).fetchone()
        if res is None:
            if layer==0: return -0.2
            if layer==1: return 0
        return res[0]


    def setstrength(self,fromid,toid,layer,strength):
        if layer==0:
            table='wordhidden'
        else:
            table='hiddenurl'
        res=self.execute('select rowid from {} where fromid={} and toid={}'.format(table,fromid,toid)).fetchone()
        if res is None:
            self.execute('insert into {}(fromid,toid,strength) values({},{},{})'.format(table,fromid,toid,strength))
        else:
            rowid=res[0]
            self.execute('update {} set strength={} where rowid={}'.format(table,strength,rowid))


    def generatehiddennode(self,wordids,urls):
        if len(wordids)>3:
            return None
        createkey='_'.join(sorted([str(wi) for wi in wordids]))
        res=self.execute("select rowid from hiddennode where create_key='{}'".format(createkey)).fetchone()
        if res is None:
            cur=self.execute("insert into hiddennode(create_key) values('{}')".format(createkey))
            hiddenid=cur.lastrowid
            for wordid in wordids:
                self.setstrength(wordid,hiddenid,0,1/len(wordids))
            for urlid in urls:
                self.setstrength(hiddenid,urlid,1,0.1)
            self._conn.commit()


    def getallhiddenids(self,wordids,urlids):
        l1={}
        for wordid in wordids:
            cur=self.execute('select toid from wordhidden where fromid={}'.format(wordid))
            for row in cur: l1[row[0]]=1
        for urlid in urlids:
            cur=self.execute('select fromid from hiddenurl where toid={}'.format(urlid))
            for row in cur: l1[row[0]]=1
        return l1.keys()


    def setupnetwork(self,wordids,urlids):
        self.wordids=wordids
        self.hiddenids=self.getallhiddenids(wordids,urlids)
        self.urlids=urlids

        self.ai=[1.0]*len(self.wordids)
        self.ah=[1.0]*len(self.hiddenids)
        self.ao=[1.0]*len(self.urlids)

        self.wi=[[self.getstrength(wordid,hiddenid,0) for hiddenid in self.hiddenids] for wordid in self.wordids]
        self.wo=[[self.getstrength(hiddenid,urlid,1) for urlid in self.urlids] for hiddenid in self.hiddenids]


    def feedforward(self):
        for i in range(len(self.wordids)):
            self.ai[i]=1.0

        for j in range(len(self.hiddenids)):
            sum=0
            for i in range(len(self.wordids)):
                sum+=self.ai[i]*self.wi[i][j]
            self.ah[j]=tanh(sum)

        for k in range(len(self.urlids)):
            sum=0
            for j in range(len(self.hiddenids)):
                sum+=self.ah[j]*self.wo[j][k]
            self.ao[k]=tanh(sum)

        return self.ao[:]


    def getresult(self,wordids,urlids):
        self.setupnetwork(wordids,urlids)
        return self.feedforward()