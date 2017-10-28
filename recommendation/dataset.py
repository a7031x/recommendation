import os
import options
import feedparser
import re
import sys

# A dictionary of movie critics and their ratings of a small
# set of movies
critics={
    'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 'The Night Listener': 3.0},
    'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 3.5},
    'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0, 'Superman Returns': 3.5, 'The Night Listener': 4.0},
    'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0, 'The Night Listener': 4.5, 'Superman Returns': 4.0, 'You, Me and Dupree': 2.5},
    'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0, 'You, Me and Dupree': 2.0},
    'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
    'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}
}


def load_movie_lens():
    folder = os.path.join(options.FLAGS.input_dir, 'ml-100k')
    movies = {}
    for line in open(os.path.join(folder, 'u.item')):
        id, title = line.split('|')[0:2]
        movies[id] = title

    prefs = {}
    for line in open(os.path.join(folder, 'u.data')):
        user, movie_id, rating, _ = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movie_id]] = float(rating)

    return prefs


def getwords(html):
    # Remove all the HTML tags
    txt = re.compile(r'<[^>]+>').sub('', html)
    # Split words by all non-alpha characters
    words = re.compile(r'[^A-Z^a-z]+').split(txt)

    return [word.lower() for word in words if word!='']


def getwordcounts(url):
    d = feedparser.parse(url)
    wc = {}

    for e in d.entries:
        if 'summary' in e: summary=e.summary
        else: summary=e.description

        words = getwords(e.title+' '+summary)
        for word in words:
            wc.setdefault(word,0)
            wc[word] += 1

    return d.feed.title if 'title' in d.feed else url.strip(' \t\n\r/'), wc


def generate_blog_data():
    apcount = {}
    wordcounts = {}
    feedlist = []
    path = os.path.join(options.FLAGS.input_dir, 'feedlist.txt')
    with open(path, 'r') as file:
        for feedurl in file:
            feedurl = feedurl.strip(' \t\n\r')
            print('processing {}'.format(feedurl))
            feedlist.append(feedurl)
            title, wc = getwordcounts(feedurl)
            wordcounts[title] = wc
            for word, count in wc.items():
                apcount.setdefault(word, 0)
                if count > 1:
                    apcount[word] += 1

    wordlist = []
    for w, bc in apcount.items():
        frac = float(bc) / len(feedlist)
        if frac > 0.1 and frac < 0.5:
            wordlist.append(w)

    path = os.path.join(options.FLAGS.input_dir, 'blogdata.txt')
    with open(path, 'w') as out:
        out.write('Blog')
        for word in wordlist:
            out.write('\t{}'.format(word))

        out.write('\n')
        for blog, wc in wordcounts.items():
            out.write(blog)

            for word in wordlist:
                if word in wc:
                    out.write('\t{}'.format(wc[word]))
                else:
                    out.write('\t0')
            out.write('\n')