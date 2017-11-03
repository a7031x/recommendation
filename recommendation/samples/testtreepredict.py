import treepredict

#s1,s2=treepredict.divideset(treepredict.my_data,2,'yes')
#print(s1)
#print(s2)

#print(treepredict.giniimpurity(treepredict.my_data))
#print(treepredict.entropy(treepredict.my_data))
#set1,set2=treepredict.divideset(treepredict.my_data,2,'yes')
#print(treepredict.entropy(set1))
#print(treepredict.giniimpurity(set1))
#print(treepredict.entropy(set2))
#print(treepredict.giniimpurity(set2))

#tree=treepredict.buildtree(treepredict.my_data)
#treepredict.printtree(tree)
#treepredict.drawtree(tree)

#tree=treepredict.buildtree(treepredict.my_data)
#print(treepredict.classify(['(direct)', 'USA', 'yes', 5], tree))

#tree=treepredict.buildtree(treepredict.my_data)
#treepredict.prune(tree,1)
#treepredict.printtree(tree)

tree=treepredict.buildtree(treepredict.my_data)
print(treepredict.mdclassify(['google',None,'yes',None],tree))
print(treepredict.mdclassify(['google','France',None,None],tree))