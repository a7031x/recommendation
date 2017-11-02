import docclass

cl=docclass.fisherclassifier(docclass.getwords)
docclass.sampletrain(cl)
print(cl.cprob('quick', 'good'))
print(cl.fisherprob('quick rabbit', 'good'))
print(cl.fisherprob('quick rabbit','bad'))
