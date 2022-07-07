import glob
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import patches

def parse_bibtex(filename):
    """Given a bibtex filename, return a list whose elements are
    dictionaries, one per entry in the file. They keys of each
    dictionary are fields present in the bibtex entry.

    """
    string = open(filename).read()
    entry_begins = []
    for m in re.finditer("@",string): entry_begins.append(m.start())
    entry_begins.append(len(string))
    E = []
    for i in range(len(entry_begins)-1):
        entry = string[entry_begins[i]:entry_begins[i+1]]
        E.append(dict(re.findall(r'\s+(\w+)\s+=\s+\{(.*)\}',entry)))
    return E

def sanitize_authors(e):
    """Splits the authors by the phrase ' and ', and also removes things
       we do not need to deal with here.

    """
    A = e['author']
    A = A.replace("\\textbf{","")
    A = A.replace("{","")
    A = A.replace("}","")
    A = A.replace("\\~","")
    A = A.replace("\\'","")
    A = A.replace("\\`","")
    A = A.replace('\\"',"")
    A = A.replace('\\v',"")
    A = A.replace('\\c',"")
    A = A.replace('\xa0B',"")
    A = A.split(" and ")
    return A

# Parse all records
E = []
for filename in glob.glob("bib/*.bib"):
    E += parse_bibtex(filename)

# List of authors / affiliations we want in our visualization, we will
# have trouble if there are authors with the same last name
rubisco = ["Kuang-Yu Chang","Nathan Collier","Weiwei Fu","Forrest Hoffman","Trevor Keenan","Gretchen Keppel-Aleks","Charles Koven","Jitendra Kumar","David Lawrence","Yue Li","Jiafu Mao","Zelalem Mekonnen","Umakant Mishra","Keith Moore","Mingquan Mu","Robinson Negron-Juarez","James Randerson","William Riley","Xiaoying Shi","Jinyun Tang","Yaoping Wang","Min Xu","Qing Zhu"]
affiliation = ["LBNL","ORNL","UCI","ORNL","LBNL","UM","LBNL","ORNL","NCAR","UCI","ORNL","LBNL","SNL","UCI","UCI","LBNL","UCI","LBNL","ORNL","LBNL","UTK","ORNL","LBNL"]
lastname = [a.split(" ")[-1] for a in rubisco]

# Get a color per affiliation
cm = plt.get_cmap("tab10")
colors = {}
for i,a in enumerate(sorted(list(set(affiliation)))):
    colors[a] = cm.colors[i]

# We generate a dictionary of sets to check aliases, the keys are the
# last names of our project group and the set is all accetable names,
# popualted from all the bib files. You will need to go into the
# generated file and hand edit the sets to remove aliases that do not
# belong with the last name.
if not os.path.isfile("author_alias.py"):
    print("Generating author alias file...")
    alias = {}
    for e in E:
        if 'author' not in e: continue
        A = sanitize_authors(e)    
        lastA = [a.split(" ")[-1] for a in A]
        for a,b in zip(lastA,A):
            if a not in lastname: continue
            if a not in alias: alias[a] = set()
            alias[a].add(b)
    with open('author_alias.py','w') as f:
        f.write("alias = %s" % alias)
    print("Edit 'author_alias.py' to remove incorrect alias names")

# Loop through the bib entries and create edges / increment paper
# counts
from author_alias import alias
papers  = np.zeros(len(rubisco),dtype=int)
connect = np.zeros((len(rubisco),len(rubisco)),dtype=int)
for e in E:
    if 'author' not in e: continue
    A = sanitize_authors(e)    
    lastA = [a.split(" ")[-1] for a in A]
    edges = []
    for a,b in zip(lastA,A):
        if a in alias and b in alias[a]: edges.append(a)    
    for x in edges:
        a = lastname.index(x)
        papers[a] += 1
        for y in edges:
            b = lastname.index(y)
            if a <= b: continue
            connect[a,b] += 1
            
df = pd.DataFrame({'fullname':rubisco,
                   'lastname':lastname,
                   'affiliation':affiliation,
                   'papers':papers},columns=['fullname','lastname','affiliation','papers'])
df = df.sort_values(['affiliation','papers'],ignore_index=True)
affiliations = list(df.affiliation.unique())

fig,ax = plt.subplots(figsize=(10,10),tight_layout=True)
angles = []
for i,r in df.iterrows():
    ang = (i+2*affiliations.index(r.affiliation))/(len(df)+2*len(affiliations))*2*np.pi
    angles.append(ang/np.pi*180)
    x = np.cos(ang)
    y = np.sin(ang)
    if x >= 0:
        ax.text(x,y,"%2d %s" % (r.papers,r.fullname),size=16,
                va='center',ha='left',
                rotation_mode='anchor',
                rotation=ang/np.pi*180)
    else:
        ax.text(x,y,"%s %2d" % (r.fullname,r.papers),size=16,
                va='center',ha='right',
                rotation_mode='anchor',
                rotation=(ang+np.pi)/np.pi*180)
df['angles'] = angles

dang = 360/(len(df)+len(affiliations))
for i,a in enumerate(affiliations):
    dfa = df[df.affiliation==a]
    t0  = dfa.iloc[ 0].angles-1.*dang
    tf  = dfa.iloc[-1].angles+0.5*dang
    arc = patches.Arc((0,0),2*0.95,2*0.95,linewidth=8,theta1=t0,theta2=tf,color=colors[a])
    ax.add_patch(arc)

    ang = (dfa.angles.values[0]-0.6*dang)/180*np.pi
    x = np.cos(ang)
    y = np.sin(ang)
    if x >= 0:
        ax.text(x,y,"%s" % (a),size=18,color=colors[a],weight='bold',
                va='center',ha='left',
                rotation_mode='anchor',
                rotation=ang/np.pi*180)
    else:
        ax.text(x,y,"%s" % (a),size=18,color=colors[a],weight='bold',
                va='center',ha='right',
                rotation_mode='anchor',
                rotation=(ang+np.pi)/np.pi*180)

    
for a,n in enumerate(lastname):
    dfa = df[df.lastname==n]
    for b,m in enumerate(lastname):
        dfb = df[df.lastname==m]
        if connect[a,b] == 0: continue
        color = '0.5' if dfa.affiliation.values[0] == dfb.affiliation.values[0] else 'k'
        zo    = -2 if dfa.affiliation.values[0] == dfb.affiliation.values[0] else -1
        r = 0.91
        xa,ya = r*np.cos(dfa.angles/180*np.pi),r*np.sin(dfa.angles/180*np.pi)
        xb,yb = r*np.cos(dfb.angles/180*np.pi),r*np.sin(dfb.angles/180*np.pi)
        plt.plot([xa,xb],[ya,yb],'-',color=color,lw=0.1+connect[a,b]/connect.max()*8,
                 solid_capstyle='round',zorder=zo)
        
x = 1.25
ax.set_axis_off()
ax.set_xlim(-x,x)
ax.set_ylim(-x,x)
plt.savefig('author_network.pdf')
plt.close()
