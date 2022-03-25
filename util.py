import os, string, random

def mkIfNone(path):
    if not os.path.exists(path):
        if path.replace("\\","/").split("/")[-1].replace(".","")!=path.replace("\\","/").split("/")[-1]:
            path="/".join(path.replace("\\","/").split("/")[:-1])
        try:
            os.makedirs(path)
        except:
            pass

def fo(a):    
    return "{0:.2f}".format(a).ljust(15)

def fo2(a):
    return "{0:.2f}".format(a).ljust(len("{0:.2f}".format(a)))

def fo5(a):
    return "{0:.1f}".format(a).ljust(len("{0:.1f}".format(a)))

def fo6(a):
    return "{0:.4f}".format(a).ljust(len("{0:.4f}".format(a)))

def fo3(a):    
    return "{0:.6f}".format(a).ljust(15)

def fo4(a):    
    return "{0:.6f}".format(a).ljust(len("{0:.6f}".format(a)))

def splitQS(a): #split quotes and space
    l=[]
    new = True
    quote = False
    for A in a:
        if new:
            l.append("")
            new = False
        if A == ' ' and quote != True:
            new = True
        elif A == '\"':
            quote = not quote
        else:
            l[-1] += A
    return l

def rand6(length=6):
    chars = string.digits
    rand =  ''.join(random.choice(chars) for _ in range(length))
    return rand