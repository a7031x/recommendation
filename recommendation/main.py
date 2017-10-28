import recommendations
import dataset
import cluster
import numpy as np

def main():
    #dataset.generate_blog_data()
    blognames, words, data = cluster.readfile('blogdata.txt')
    kclust=cluster.kcluster(data, k=10)
    print([blognames[r] for r in kclust[2]])

main()
