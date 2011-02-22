import sys,os
import getopt
#import argparse
import Image,ImageStat
from random import randint
import random
import EXIF
from k_means_plus_plus import *
from clustering import *
from settings import *

def eval_float(e):
    if '/' in e:
        return float(e.split('/')[0])/float(e.split('/')[1])
    else:
        return int(e)

try:
    argv=sys.argv[1:]
    optlist, args = getopt.getopt(argv, ':vir:d')
    optlist=dict(optlist)

    verbose='-v' in optlist
    interactive='-i' in optlist
    num_of_repeats=int(optlist.get('-r') or 1)
    num_of_clusters=optlist.get('-c') or None
    draw='-d' in optlist

except getopt.GetoptError:
    print "usage: [-r REPEATS] [-c CLUSTERS] [-i] [-v] [-d] FILES"
    exit(-1)
    
if len(args)==0:
    print "Missing FILES parameter!"
    print "usage: [-r REPEATS] [-c CLUSTERS] [-i] [-v] [-d] FILES"
    exit(-1)

#~ parser = argparse.ArgumentParser(description='Image clustering program.')
#~ parser.add_argument('paths', metavar='FILES', type=file, nargs="+",
                   #~ help='the path to the images')
#~ parser.add_argument('--r', dest='num_of_repeat', metavar='REPEATS', default=1, type=int, help='Number of repeat clustering')
#~ parser.add_argument('--n', dest='num_of_clusters', metavar='CLUSTERS', type=int, help='Number of clusters')
#~ parser.add_argument('--i', dest='interactive', action='store_const',
                   #~ const=True, default=False, help='Interactive mode')
#~ parser.add_argument('--v', dest='verbose', action='store_const',
                   #~ const=True, default=False, help='verbose output')
#~ 
#~ args = parser.parse_args()
#~ num_of_clusters = args.num_of_clusters

if verbose:print "Extracting information from files..."
objects = []
for (counter,this_file) in enumerate(args):
    try:
        im = Image.open(this_file, 'r')
    except IOError:
        print 'File load error'
        
    else:
        stat = ImageStat.Stat(im)
        exif_data = EXIF.process_file(open(this_file, 'r'))
        
        obj = ImageObject(this_file)
        
        for e in EXIF_ATTRIBUTES:
            # Kvalitativ attributumok
            if len(e) == 1:
                try: obj.attributes[e[0]] = QualityAttr(exif_data[e[0]].printable, settings.WEIGHTS[e[0]])
                except: pass
            # kvantitativ attr-k, max ertekkel a normalashoz
            elif len(e) == 2:
                try: obj.attributes[e[0]] = QuantityAttr(eval_float(exif_data[e[0]].printable), settings.WEIGHTS[e[0]], e[1])
                except: pass
        
        #~ 
        #~ obj.attributes["EXIF DateTimeDigitized"] = DateAttr(exif_data["EXIF DateTimeDigitized"].printable, 1)
        #~         
        
        max_sum2 = (255**2)*im.size[0]*im.size[1]
        obj.attributes["sum2_R"] = QuantityAttr(stat.sum2[0], settings.WEIGHTS["sum2"], max_sum2)
        obj.attributes["sum2_G"] = QuantityAttr(stat.sum2[1], settings.WEIGHTS["sum2"], max_sum2)
        obj.attributes["sum2_B"] = QuantityAttr(stat.sum2[2], settings.WEIGHTS["sum2"], max_sum2)        
       
        obj.attributes["mean_R"] = QuantityAttr(stat.mean[0], settings.WEIGHTS["mean"], settings.max_mean)
        obj.attributes["mean_G"] = QuantityAttr(stat.mean[1], settings.WEIGHTS["mean"], settings.max_mean)
        obj.attributes["mean_B"] = QuantityAttr(stat.mean[2], settings.WEIGHTS["mean"], settings.max_mean)        
        
        obj.attributes["median_R"] = QuantityAttr(stat.median[0], settings.WEIGHTS["median"], settings.max_median)
        obj.attributes["median_G"] = QuantityAttr(stat.median[1], settings.WEIGHTS["median"], settings.max_median)
        obj.attributes["median_B"] = QuantityAttr(stat.median[2], settings.WEIGHTS["median"], settings.max_median)        
        
        obj.attributes["rms_R"] = QuantityAttr(stat.rms[0], settings.WEIGHTS["rms"], settings.max_rms)
        obj.attributes["rms_G"] = QuantityAttr(stat.rms[1], settings.WEIGHTS["rms"], settings.max_rms)
        obj.attributes["rms_B"] = QuantityAttr(stat.rms[2], settings.WEIGHTS["rms"], settings.max_rms)
                
        obj.attributes["var_R"] = QuantityAttr(stat.var[0], settings.WEIGHTS["var"], settings.max_var)
        obj.attributes["var_G"] = QuantityAttr(stat.var[1], settings.WEIGHTS["var"], settings.max_var)
        obj.attributes["var_B"] = QuantityAttr(stat.var[2], settings.WEIGHTS["var"], settings.max_var)
        
        objects.append(obj)
        
        if verbose: print "%s (%s of %s)" % (this_file, counter+1, len(args))

if verbose:print 'File processing complete.\n'
if len(objects)==0:
    print "Files not found! (Perhaps wrong parameter used)"
    print "usage: [-r REPEATS] [-c CLUSTERS] [-i] [-v] [-d] FILES"
    exit(-1)

while True:
    if interactive:
        user_input=raw_input('<type "x" to exit>\nPress ENTER to start..(or type a num to custom num of clusters): ')
        if user_input=='x':exit(0)
        try:        
            num_of_clusters = int(user_input)
        except:
            num_of_clusters = num_of_clusters

    if not num_of_clusters:
        num_of_clusters = int(math.sqrt(len(objects)/2))
    
    result_stat={}
    best_clustering=None
    best_clustering_error=Decimal('Infinity')
    for i in range(num_of_repeats):
        if verbose:print '-----------------------------------'
        if verbose:print 'Repeat %s of %s' % (str(i+1),str(num_of_repeats))
        if verbose:print '-----------------------------------'
        #kmeans++
        initial_clusters=do_kmeans_plus_plus(objects,num_of_clusters)
        
        #random
        #initial_clusters=[[o] for o in random.sample(objects,num_of_clusters)]
        
        clustering = KMeans(initial_clusters)
        results = clustering.execute(objects, verbose)
        error = clustering.total_squared_error()
        if verbose: print 'clustering error:',error
        
        if error < best_clustering_error:
            best_clustering = deepcopy(clustering)
            best_clustering_error = error
        
    if verbose:print '-----------------------------------'
    if verbose:print 'best clusterings total sqared error: ',best_clustering.total_squared_error()
    if verbose:print '-----------------------------------'
    
    if verbose:print 'Results:'
    for r in best_clustering.results:
        print r.filename
    
    if draw:
        if verbose:print 'Drawing index image...'
        best_clustering.draw_clusters(results = best_clustering.results)
        if verbose:print 'Index image saved.'
    if not interactive:
        break


