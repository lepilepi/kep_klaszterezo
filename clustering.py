import Image
import ImageDraw
import math
from decimal import *
from datetime import datetime
from datetime import timedelta
from copy import deepcopy
from time import *

import settings

'''
yuml.me
[Object|+attributes|+get_distance(vector){bg:green}]^[ImageObject|+filename;+path{bg:green}]
[ClusteringAlgorithm|-clusters|-get_get_ref_point(cluster);+execute(objects){bg:orange}]^[KMeans||-iterate(objects){bg:orange}]
[ClusteringAlgorithm]<>1-0..*>[Object]

'''
def avg_time(a):
    epoch = datetime.fromtimestamp(mktime(gmtime(0)))

    numdeltas = len(a)
    sumdeltas = timedelta(seconds=0)
    
    for i in a:
        delta = abs(i-epoch)
        try:
            sumdeltas += delta
        except:
            raise
    avg = sumdeltas / numdeltas
    return epoch+avg
    
class Attribute():
    value = None
    weight = None
    
    def __init__(self,value,weight):
        self.value = value
        self.weight = weight
    
    def divide(self,n):
        raise NotImplementedError( "Should have implemented this" )

    def compare(self,Attribute):
        raise NotImplementedError( "Should have implemented this" )

class QuantityAttr(Attribute):
    max_value = None
    
    def __init__(self,value,weight, max_value):
        Attribute.__init__(self,value,weight)
        self.max_value = max_value
        self.value = min(float(value)/max_value, 1)
    
    def add(self,other):
        self.value+=other.value
        
    def divide(self,n):
        self.value/=n
        
    def compare(self,other):
        return self.value-other.value

class QualityAttr(Attribute):
    
    def __init__(self,value,weight):
        Attribute.__init__(self,value,weight)
        self.value = {value:1}
        
    def add(self,other):
        for k,v in other.value.items():
            if k in self.value:
                self.value[k]+=v
            else:
                self.value[k]=v
    
    def divide(self,n):
        pass
    
    def compare(self,other):
        d=deepcopy(other.value)
        m=max(v for k,v in other.value.items())
        for k,v in d.items():
            d[k]=abs(float(v-m))/m
            
        #print d
        #print self.value.items()
        my_key = self.value.items()[0][0]
        if my_key in d:
            #print d[my_key]
            return d[my_key]
        else:
            #print 1
            return 1

        #return [1,0][self.value==other.value]

class DateAttr(Attribute):
    format = None
    
    datetimes = []
    
    def __init__(self,value,weight,format='%Y:%m:%d %H:%M:%S'):
        Attribute.__init__(self,value,weight)
        self.format = format
        self.datetimes=[datetime.strptime(self.value,self.format)]
    
    def add(self, other):
        self.datetimes.append(datetime.strptime(other.value,other.format))
        
    def divide(self,n):
        #self.datetimes.sort()
        self.value = avg_time(self.datetimes).strftime('%Y:%m:%d %H:%M:%S')
        
        #self.value = (min(self.datetimes) + (max(self.datetimes)-min(self.datetimes))/2 ).strftime('%Y:%m:%d %H:%M:%S')
        self.datetimes=[datetime.strptime(self.value,self.format)]
    
    def compare(self,other):
        d1 = datetime.strptime(self.value,self.format)
        d2 = datetime.strptime(other.value,other.format)
        d = abs(d2-d1)
        diff = d.days + d.seconds
        #normalt ertke a kolonbsegnek mp alapjan, a globalis DATE_MAX ertek szerint levagva
        return min(float(diff)/settings.DATE_MAX, 1)



class Object():
    attributes = {}
    
    def __init__(self):
        self.attributes = {}
        
    def get_distance(self,other):
        # distance = sqrt(((P1-Q1)^2 + (P1-Q1)^2 + ... + (Pn-Qn)^2)/n)
        
        s=0
        n=0
        for (k,a1) in self.attributes.items():
            if other.get(k):
                n+=1
                a2 = other.get(k)
                d=(a1.compare(a2))**2
                d*=a1.weight
                s+=d
        return math.sqrt(s/n)
        

class ImageObject(Object):
    filename=''
    
    def __init__(self, filename):
        Object.__init__(self)
        self.filename = filename

class ClusteringAlgorithm():
    clusters=[]
    results = []
    
    def __init__(self, clusters):
        self.clusters= clusters
        
    def get_ref_point(self,cluster):
        pass
    
    def execute(self, objects, verbose):
        pass
    
    def draw_clusters(self,results=None):
        WIDTH = 1000
        HEIGHT = 30
        for cluster in self.clusters:
            HEIGHT+=(int((len(cluster)*110)/WIDTH)+1)*110 + 30
        
        out = Image.new('RGBA', (WIDTH,HEIGHT))
        draw = ImageDraw.Draw(out)
        x=10
        y=10
        for n, cluster in zip(range(len(self.clusters)), self.clusters):
            draw.rectangle((0, y-2, WIDTH, y+12), fill=128)
            draw.text((x,y),'Cluster #%s (%s objects)' % (n,len(cluster)))
            y+=20
            for o in cluster:
                if x>=WIDTH-110:
                    x = 10
                    y+= 110
                im = Image.open(o.filename)
                im.thumbnail((100,100), Image.ANTIALIAS)
                if o in results:
                    draw.rectangle(((x-5,y-5),(x+105,y+105)),255)
                out.paste(im, (x,y))
                draw.text((x,y),o.filename.split("/")[-1])
                x+=100+10
            x=10
            y+=110
                
        #out.show()
        out.save("index.jpg", "JPEG")


    def total_squared_error(self):
        e=0
        for cluster in self.clusters:
            rf = self.get_ref_point(cluster)
            for o in cluster:
                e+=o.get_distance(rf)**2
        return e
        
class KMeans(ClusteringAlgorithm):
    
    def get_ref_point(self,cluster):
        
        ref_point={}
        for o in cluster:
            for k,v in o.attributes.items():
                if k in ref_point:
                    ref_point[k].add(v)
                else:
                    ref_point[k]=deepcopy(v)
        
        for k,v in ref_point.items():
            ref_point[k].divide(len(cluster))
        
        return ref_point

    def iterate(self,objects):
        changes = 0
        for o in objects:
            min_distance=Decimal('Infinity')
            closest_cluster=None
            
            for c in self.clusters:
                rf = self.get_ref_point(c)
                if o.get_distance(rf)<min_distance:
                    min_distance = o.get_distance(rf)
                    closest_cluster=c
            
            try:
                closest_cluster.index(o)
            except ValueError:
                #kivesz mindenhonnan
                for cl in self.clusters:
                    try:
                        cl.remove(o)
                        #print '%s-t kivesz #%s-bol' % (o.filename,self.clusters.index(cl))
                    except ValueError:
                        pass
                #beletesz ide
                closest_cluster.append(o)
                #print '%s-t betesz #%s-be' % (o.filename,self.clusters.index(closest_cluster))
                changes+=1
                
        return changes
        
    def execute(self, objects, verbose):
        for i in range(100):
            if verbose == True: print "iteration", i
            ch = self.iterate(objects)
            if verbose == True: print ch, "changes"
            if ch==0: break
            if verbose == True: print [len(c) for c in self.clusters]
        
        #~ top_cluster = max([(len(c),c) for c in self.clusters])[1]
        #~ ref_point = self.get_ref_point(top_cluster)
        #~ closest_to_ref_point = min([(o.get_distance(ref_point),o) for o in top_cluster])[1]
        #~ return closest_to_ref_point
        
        if verbose: print 'Min cluster size:' , len(objects)*settings.MIN_SIZE_OF_RELEVANT_CLUSTER
        results = []
        top_clusters = []
        for (counter,c) in enumerate(self.clusters):
            if len(c)>=len(objects)*settings.MIN_SIZE_OF_RELEVANT_CLUSTER:
                top_clusters.append(c)
                
                ref_point = self.get_ref_point(c)
                closest_to_ref_point = min([(o.get_distance(ref_point),o) for o in c])[1]
                results.append(closest_to_ref_point)
                
                if verbose: print 'Cluster #%s size: %s ---> %s' % (str(counter), str(len(c)), closest_to_ref_point.filename)
            else:
                if verbose: print 'Cluster #%s size: %s' % (str(counter), str(len(c)))
        
        #~ for c in top_clusters:
            #~ ref_point = self.get_ref_point(c)
            #~ closest_to_ref_point = min([(o.get_distance(ref_point),o) for o in c])[1]
            #~ results.append(closest_to_ref_point)
        
        if len(results)==0:
            max_cluster = max([(len(c),c,counter) for (counter,c) in enumerate(self.clusters)])
            top_cluster = max_cluster[1]
            ref_point = self.get_ref_point(top_cluster)
            closest_to_ref_point = min([(o.get_distance(ref_point),o) for o in top_cluster])[1]
            results = [closest_to_ref_point]
            if verbose: print 'Cluster #%s size: %s ---> %s' % (max_cluster[2], str(len(top_cluster)), closest_to_ref_point.filename)
            
        self.results = results
        return results


