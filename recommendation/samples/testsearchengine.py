import searchengine

#pagelist=['http://www.baidu.com']
#crawler=searchengine.crawler('')
#crawler.crawl(pagelist)

e=searchengine.searcher('searchindex.db')
r=e.query('baidu music')
print(r)