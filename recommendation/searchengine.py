from urllib import request
from urllib import parse
from bs4 import BeautifulSoup
from sqlite3 import dbapi2 as sqlite

class crawler:
    def __init__ (self, dbname):
        pass


    def __del__ (self):
        pass


    def dbcommit(self):
        pass


    def get_entry_id(self, table, field, value, create_new=True):
        return None


    def add_to_index(self, url, soup):
        print('Indexing %s' % url)


    def get_text_only(self, soup):
        return None


    def separate_words(self, text):
        return None


    def is_indexed(self, url):
        return False


    def add_link_ref(self, url_from, url_to, link_text):
        pass


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


    def create_index_tables(self):
        pass

