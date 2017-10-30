import recommendations
import dataset
import cluster
import numpy as np
from urllib import request
from bs4 import BeautifulSoup
import re

chare = re.compile(r'[!-\.&]')
itemowners = {}

dropwords = ['a', 'new', 'some', 'more', 'my', 'own', 'the', 'many', 'other', 'another']
currentuser = 0

c = request.urlopen('http://finance.china.com.cn/hz/sh/2345/20171028/15862.shtml')
soup = BeautifulSoup(c.read(), "html5lib")
for td in soup('td'):

links = soup('a')
print(links[10])
print(links[10]['href'])
