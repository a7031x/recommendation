import searchengine
import nn
#pagelist=['http://www.baidu.com']
#crawler=searchengine.crawler('')
#crawler.crawl(pagelist)

#e=searchengine.searcher('searchindex.db')
#r=e.query('baidu music')
#print(r)

#crawler=searchengine.crawler('searchindex.db')
#crawler.calculatepagerank()

#crawler=searchengine.crawler('searchindex.db')
#e=searchengine.searcher('searchindex.db')
#cur=crawler.execute('select * from pagerank order by score desc')
#r=[x for x in cur][0:5]
#r=[(e.get_url_name(x),s) for x,s in r]
#print(r)

mynet=nn.searchnet('nn.db')
#mynet.maketables()
