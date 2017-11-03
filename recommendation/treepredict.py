from PIL import Image,ImageDraw
import options
import os

#Referrer|Location|Read FAQ|Pages viewed|Service chosen
my_data=[['slashdot','USA','yes',18,'None'],
        ['google','France','yes',23,'Premium'],
        ['digg','USA','yes',24,'Basic'],
        ['kiwitobes','France','yes',23,'Basic'],
        ['google','UK','no',21,'Premium'],
        ['(direct)','New Zealand','no',12,'None'],
        ['(direct)','UK','no',21,'Basic'],
        ['google','USA','no',24,'Premium'],
        ['slashdot','France','yes',19,'None'],
        ['digg','USA','no',18,'None'],
        ['google','UK','no',18,'None'],
        ['kiwitobes','UK','no',19,'None'],
        ['digg','New Zealand','yes',12,'Basic'],
        ['slashdot','UK','no',21,'None'],
        ['google','UK','yes',18,'Basic'],
        ['kiwitobes','France','yes',19,'Basic']]


class decisionnode:
    def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
        self.col=col
        self.value=value
        self.results=results
        self.tb=tb
        self.fb=fb


def divideset(rows,column,value):
    if isinstance(value,int) or isinstance(value,float):
        split_function=lambda row:row[column]>=value
    else:
        split_function=lambda row:row[column]==value

    set1=[row for row in rows if split_function(row)]
    set2=[row for row in rows if not split_function(row)]
    return set1,set2


def uniquecounts(rows):
    results={}
    for row in rows:
        r=row[len(row)-1]
        if r not in results:
            results[r]=0
        results[r]+=1
    return results


def giniimpurity(rows):
    total=len(rows)
    counts=uniquecounts(rows)
    imp=0
    for k1 in counts:
        p1=counts[k1]/total
        for k2 in counts:
            if k2==k1:
                continue
            p2=counts[k2]/total
            imp+=p1*p2
    return imp


def entropy(rows):
    from math import log
    log2=lambda x:log(x)/log(2)
    results=uniquecounts(rows)
    ent=0
    for r in results:
        p=results[r]/len(rows)
        ent-=p*log2(p)
    return ent


def buildtree(rows,scoref=entropy):
    if len(rows)==0:
        return decisionnode()
    current_score=scoref(rows)
    best_gain=0
    best_criteria=None
    best_sets=None

    column_count=len(rows[0])-1
    for col in range(column_count):
        column_values={}
        for row in rows:
            column_values[row[col]]=1
        for value in column_values:
            set1,set2=divideset(rows,col,value)
            p=len(set1)/len(rows)
            gain=current_score-p*scoref(set1)-(1-p)*scoref(set2)
            if gain>best_gain and len(set1)>0 and len(set2)>0:
                best_gain=gain
                best_criteria=col,value
                best_sets=set1,set2
    if best_gain>0:
        true_branch=buildtree(best_sets[0])
        false_branch=buildtree(best_sets[1])
        return decisionnode(col=best_criteria[0],value=best_criteria[1],tb=true_branch,fb=false_branch)
    else:
        return decisionnode(results=uniquecounts(rows))


def printtree(tree,indent=''):
    if tree.results is not None:
        print(indent+str(tree.results))
    else:
        print(indent+'{}:{}?'.format(tree.col,tree.value))
        print(indent+'T->')
        printtree(tree.tb,indent+'  ')
        print(indent+'F->')
        printtree(tree.fb,indent+'  ')


def getwidth(tree):
    if tree.tb is None and tree.fb is None:
        return 1
    else:
        return getwidth(tree.tb)+getwidth(tree.fb)


def getdepth(tree):
    if tree.tb is None and tree.fb is None:
        return 0
    else:
        return max(getdepth(tree.tb),getdepth(tree.fb))+1


def drawtree(tree,jpeg='tree.jpg'):
    jpeg=os.path.join(options.FLAGS.output_dir,jpeg)
    w=getwidth(tree)*100
    h=getdepth(tree)*100+120
    img=Image.new('RGB', (w,h),(255,255,255))
    draw=ImageDraw.Draw(img)
    drawnode(draw,tree,w/2,20)
    img.save(jpeg,'JPEG')


def drawnode(draw,tree,x,y):
    if tree.results==None:

        w1=getwidth(tree.fb)*100
        w2=getwidth(tree.tb)*100

        left=x-(w1+w2)/2
        right=x+(w1+w2)/2

        draw.text((x-20,y-10),str(tree.col)+':'+str(tree.value),(0,0,0))

        draw.line((x,y,left+w1/2,y+100),fill=(255,0,0))
        draw.line((x,y,right-w2/2,y+100),fill=(255,0,0))

        drawnode(draw,tree.fb,left+w1/2,y+100)
        drawnode(draw,tree.tb,right-w2/2,y+100)
    else:
        txt=' \n'.join(['%s:%d'%v for v in tree.results.items()])
        draw.text((x-20,y),txt,(0,0,0))


def classify(observation,tree):
    if tree.results is not None:
        return tree.results
    else:
        v=observation[tree.col]
        branch=None
        if isinstance(v,int) or isinstance(v,float):
            if v>=tree.value:
                branch=tree.tb
            else:
                branch=tree.fb
        else:
            if v==tree.value:
                branch=tree.tb
            else:
                branch=tree.fb
        return classify(observation,branch)


def prune(tree,mingain):
    if tree.tb.results is None:
        prune(tree.tb,mingain)
    if tree.fb.results is None:
        prune(tree.fb,mingain)

    if tree.tb.results is not None and tree.fb.results is not None:
        tb,fb=[],[]
        for v,c in tree.tb.results.items():
            tb+=[[v]]*c
        for v,c in tree.fb.results.items():
            fb+=[[v]]*c
        delta=entropy(tb+fb)-(entropy(tb)+entropy(fb))/2
        if delta<mingain:
            tree.tb,tree.fb=None,None
            tree.results=uniquecounts(tb+fb)