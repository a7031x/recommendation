import os
import options
from math import sqrt
from PIL import Image, ImageDraw
import numpy as np
import random

def readfile(filename):
    filename = os.path.join(options.FLAGS.input_dir, filename)
    with open(filename) as file:
        lines = [line.strip() for line in file]
        columns = lines[0].split('\t')[1:]
        rownames = []
        data = []
        for line in lines[1:]:
            p = line.split('\t')
            rownames.append(p[0])
            data.append([float(x) for x in p[1:]])
        return rownames, columns, data


def pearson(v1, v2):
    sum1 = sum(v1)
    sum2 = sum(v2)
    sum1_2 = sum([x*x for x in v1])
    sum2_2 = sum([x*x for x in v2])
    n = len(v1)
    assert(len(v2) == n)

    xsum = sum([x*y for x, y in zip(v1, v2)])
    num = xsum - sum1 * sum2 / n
    den = sqrt((sum1_2 - sum1 * sum1 / n) * (sum2_2 - sum2 * sum2 / n))
    if 0 == den:
        return 0
    else:
        return 1.0 - num / den


class bicluster:
    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        self._left = left
        self._right = right
        self._vec = vec
        self._id = id
        self._distance = distance


def hcluster(rows, distance=pearson):
    distances = {}
    currentclustid = -1
    clust = [bicluster(rows[i], id=i) for i in range(len(rows))]
    while len(clust) > 1:
        lowestpair = (0, 1)
        closest = distance(clust[0]._vec, clust[1]._vec)

        for i in range(len(clust)):
            for j in range(i + 1, len(clust)):
                if (clust[i]._id, clust[j]._id) not in distances:
                    distances[(clust[i]._id, clust[j]._id)] = distance(clust[i]._vec, clust[j]._vec)
                d = distances[(clust[i]._id, clust[j]._id)]
                if d < closest:
                    closest = d
                    lowestpair = (i, j)
        mergevec = [(clust[lowestpair[0]]._vec[i] + clust[lowestpair[1]]._vec[i]) / 2.0 for i in range(len(clust[0]._vec))]
        newcluster = bicluster(mergevec, left=clust[lowestpair[0]], right=clust[lowestpair[1]], distance=closest, id=currentclustid)
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    return clust[0]


def kcluster(rows, distance=pearson, k=4):
    # Determine the minimum and maximum values for each point
    num_columns = len(rows[0])
    ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(num_columns)]

  # Create k randomly placed centroids
    clusters = [[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0] for i in range(num_columns)] for j in range(k)]

    lastmatches=None
    for t in range(100):
        print('Iteration %d' % t)
        bestmatches=[[] for i in range(k)]

    # Find which centroid is the closest for each row
        for j in range(len(rows)):
            row=rows[j]
            bestmatch=0
            for i in range(k):
                d=distance(clusters[i], row)
                if d<distance(clusters[bestmatch],row):
                    bestmatch=i
            bestmatches[bestmatch].append(j)

        # If the results are the same as last time, this is complete
        if bestmatches==lastmatches:break
        lastmatches=bestmatches

        # Move the centroids to the average of their members
        for i in range(k):
            avgs=[0.0]*num_columns
            if len(bestmatches[i])>0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m]+=rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j]/=len(bestmatches[i])
            clusters[i]=avgs

    return bestmatches


def print_cluster(clust, labels=None, n=0):

    prefix = ' ' * n
    if clust._id < 0:
        print(prefix + '-')
    else:
        if labels == None:
            print(prefix + str(clust._id))
        else:
            print(prefix + str(labels[clust._id]))

    if clust._left != None:
        print_cluster(clust._left, labels, n+1)
        print_cluster(clust._right, labels, n+1)


def get_height(clust):
    if clust._left is None and clust._right is None:
        return 1
    else:
        return get_height(clust._left) + get_height(clust._right)


def get_depth(clust):
    if clust._left is None and clust._right is None:
        return 0
    else:
        return max(get_depth(clust._left), get_depth(clust._right)) + clust._distance


def draw_node(draw, clust, x, y, scaling, labels):
    if clust._id < 0:
        h1 = get_height(clust._left) * 20
        h2 = get_height(clust._right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2
        # Line length
        ll = clust._distance * scaling
        # Vertical line from this cluster to children
        draw.line((x,top + h1 / 2,x,bottom - h2 / 2),fill=(255,0,0))

        # Horizontal line to left item
        draw.line((x,top + h1 / 2,x + ll,top + h1 / 2),fill=(255,0,0))

        # Horizontal line to right item
        draw.line((x,bottom - h2 / 2,x + ll,bottom - h2 / 2),fill=(255,0,0))
        # Call the function to draw the left and right nodes
        draw_node(draw,clust._left,x + ll,top + h1 / 2,scaling,labels)
        draw_node(draw,clust._right,x + ll,bottom - h2 / 2,scaling,labels)
    else:
        # If this is an endpoint, draw the item label
        draw.text((x + 5,y - 7),labels[clust._id],(0,0,0))


def draw_dendrogram(clust, labels, jpeg='clusters.jpg'):
    jpeg = os.path.join(options.FLAGS.output_dir, jpeg)
    h = get_height(clust) * 20
    w = 1200
    depth = get_depth(clust)
    scaling = float(w - 150) / depth
    image = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.line((0, h/2, 10, h/2), fill=(255, 0, 0))
    draw_node(draw, clust, 10, (h / 2), scaling, labels)
    image.save(jpeg, 'JPEG')

