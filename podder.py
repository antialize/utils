#!/usr/bin/python
import smtplib
import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

import libxml2
from urllib import urlopen
import os
from subprocess import call,Popen, PIPE
from os import listdir,mkdir,remove
from multiprocessing import Pool
from tempfile import NamedTemporaryFile
from hashlib import sha1
from conf import *

def getext(file):
    mimemap = {"video/mp4": "mp4", "video/x-flv": "flv", "video/quicktime" : "mov",
               "application/ogg": "ogg", "video/x-ms-asf": "asf", 
               "video/x-msvideo": "avi", "application/vnd.rn-realmedia": "rm"}
    mimetype = Popen(["file",'-b','--mime-type',file], stdout=PIPE).communicate()[0].strip()
    if mimetype in mimemap: return mimemap[mimetype]
    magic = Popen(["file",'-b',file], stdout=PIPE).communicate()[0].strip()
    if magic == "Matroska data": return "mkv"
    return "mpg"


def fixname(name):
    return name.replace("\\","_").replace("#","_").replace("!","_").replace("/","-")

#def tomkv(src, dst):
    #If mkvmerge works just use that
#    if call(["mkvmerge", src, '-q', '-o', dst]) == 0: return True
    #If not we will use mencoder
#    tmp = sha1(dst).hexdigest()
#    if call(["mencoder",src,"-really-quiet","-oac","copy","-ovc","copy","-o",tmp]) != 0: return False
    #The output of mencoder does not seem to be propperly muxed
#    if call(["mkvmerge",tmp, '-q', '-o', dst]) != 0: return False
#    remove(tmp)
#    return True

def youtubedownload(src, dst):
    tmp = sha1(src).hexdigest()
    print "Fetching %s"%dst
    if call(["youtube-dl",src,'-c', '-b','-q', '-o', tmp]) != 0: return False
    os.rename(tmp,dst+"."+getext(tmp))
    #print "mkv'ing %s"%dst
    #if not tomkv(tmp, dst): return False
    #remove(tmp)
    return True

def downloadwget(src, dst):
    tmp = sha1(src).hexdigest()
    print "Fetching %s"%dst
    if call(["wget", src, '-c', "-q", "-O", tmp]) != 0: return False
    os.rename(tmp,dst+"."+getext(tmp))
    #print "mkv'ing %s"%dst
    #if not tomkv(tmp, dst): return False
    #remove(tmp)
    return True


def downloadday9(pool):
    global vf
    doc = libxml2.parseDoc(urlopen("http://day9tv.blip.tv/rss").read())
    ctxt = doc.xpathNewContext()
    
    files = set([ x.rsplit(".",1)[0] for x in listdir("day9_daily")])
    files2 = set([ x.rsplit(".",1)[0] for x in listdir("day9")])
    o=""
    n=0
    for x in reversed(ctxt.xpathEval("//item")):
        url = x.xpathEval("enclosure/@url")
        title = x.xpathEval("title")
        if url and title:
            t = fixname(title[0].getContent().replace("D9D ","").replace("Day[9] Daily #","").replace("-"," ",1))
            t = t.split(" ",1)
        daily=False
        try:
            t = "%03d - %s"%(int(t[0]),t[1].strip())
            daily=True
        except:
            pass
        
        if daily:
            if not t in files:
                src = url[0].getContent()
                vf.append( ("day9", t) )
                pool.apply_async(downloadwget, (src,"day9_daily/"+t))
        else:
            pass
            # t = title[0].getContent()
            # x = t.split(" Game")[0].split("(")[0].strip(" 0123456789-")
            # if x != o:
            #     n+=1
            #     o=x
            # t = "%04d %s"%(n,t) 
            # if not t in files2:
            #     src = url[0].getContent()
            #     vf.append( ("day9", t) )
            #     pool.apply_async(downloadwget, (src,"day9/"+t))
    
def downloadyoutubeuser(pool, user):
    global vf
    print "========================> %s <==========================="%user
    doc = libxml2.parseDoc(urlopen("http://gdata.youtube.com/feeds/base/users/%s/uploads?alt=rss&v=1&orderby=published"%user).read())
    ctxt = doc.xpathNewContext()
        
    videos = []
    for x in ctxt.xpathEval("//item"):
        url = x.xpathEval("link")
        title = x.xpathEval("title")
        if url and title:
            videos.append( (url[0].getContent(), fixname(title[0].getContent())) )

            try: mkdir(user) 
            except Exception: pass
        
    videos.reverse()    
    dir = listdir(user)
    numtoname = {}
    nametonum = {'dummy':0}
    numtofullname = {}
    for x in dir:
        n, name = x.split(' - ',1)
        numtofullname[int(n)] = name
        name = name.rsplit(".",1)[0]
        numtoname[int(n)] = name
        nametonum[name] = int(n)

    if videos[0][1] in nametonum: video=nametonum[videos[0][1]]
    else: video=max(nametonum.values())+1

    i=0
    while i < len(videos) or (i+video) in numtoname:
        v = (i+video)
        if v in numtoname and i < len(videos) and numtoname[v] == videos[i][1]: 
            i += 1
            continue

        if v in numtoname: 
            remove("%s/%04d - %s"%(user,v,numtofullname[v]))

        if i < len(videos): 
            vf.append( (user, "%04d - %s"%(v,videos[i][1])) )
            pool.apply_async(youtubedownload, (videos[i][0],"%s/%04d - %s"%(user,v,videos[i][1])))
            #youtubedownload(videos[i][0],"%s/%04d - %s"%(user,v,videos[i][1]))
        i += 1

if __name__ == '__main__':
    vf=[]
    pool = Pool(processes=6)
    downloadday9(pool)
    #users=['HuskyStarcraft','grethsc','HDstarcraft', 'moletrap', 'VioleTak', 'diggitySC' ]
    #for user in users:
    #    downloadyoutubeuser(pool, user)

    pool.close()
    pool.join()

    if vf:
        msg = MIMEMultipart()
        msg['Subject'] = "Podder"
        msg['From'] = from_addr
        msg['To'] = to_addr
        m = "Videos where fetched by podder\n\n"+"\n".join([ ": ".join(x) for x in vf])+"\n"
        msg.attach(MIMEText(m))
        smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp.login(gmail_user, gmail_pass)
        smtp.sendmail(from_addr, to_addr, msg.as_string())

