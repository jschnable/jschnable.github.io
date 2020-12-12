def parse_authors(afile):
    fh = open(afile)
    fh.readline()
    lookup_author = {}
    info_author = {}
    for x in fh:
        y = x.strip().split(',')
        mynames = [y[0]]
        if len(y[2]) != 0:
            mynames.extend(y[2].split(";"))
        mynames2 = []
        for aname in mynames:
            mynames2.append(aname.replace(' ',''))
#        mynames = mynames2
        myinfo = {'name':y[1],'filename':y[3],'citation':y[0],'aliases':y[2]}
        info_author[y[1]] = myinfo
        for aname in mynames:
            lookup_author[aname] = y[1]
        print(y[1],mynames)
    return lookup_author,info_author

class paper:
    def __init__(self,paperstring):
        self.citation = paperstring
        auth_string = paperstring.split("(")[0].replace('<b>','**').replace('</b>','**').replace('*','').split(',')
        auth_string_cleaned = []
        for x in auth_string:
            auth_string_cleaned.append(x.lstrip().strip())
        self.authors = auth_string_cleaned
        try:
            myyear = paperstring.split('(')[1].split(')')[0]
        except:
            print("Missing Year",paperstring)
            return
        if len(myyear) != 4:
            if len(paperstring.split("(")) >= 3:
                myyear = paperstring.split('(')[2].split(')')[0]
            else:
                myyear =  "Preprint"
        self.year = myyear
        try:
            titlelink = paperstring.split('"')[1]
        except:
            print("Missing Quotes",paperstring)
            return
        try:
            mytitle = titlelink.split("[")[1].split(']')[0]
            self.title = mytitle
            myurl = titlelink.split("(")[1].split(')')[0]
            self.url = myurl
        except:
            try:
                titlelink = paperstring.split('href="')[1].split('</a>')[0]
                mytitle = titlelink.split('>')[1]
                myurl = titlelink.split('>')[0].replace('"','')
                self.title = mytitle
                self.url = myurl
            except:
                print("Missing Title",paperstring)
                return
        posttitle = paperstring.split('"')[2]
        try:
            myjournal = posttitle.split('*')[1]
        except:
            try:
                posttitle = paperstring.split('a>')[1]
                myjournal = posttitle.split("<i>")[1].split('</i>')[0]
            except:
                print("Missing Journal",paperstring)
                return
        self.journal = myjournal
        a = posttitle.split()
        mydoi = ''
        for xind,x in enumerate(a):
            if x == 'doi:' or x == 'doi':
                mydoi = a[xind+1]
        self.doi = mydoi

alookup,ainfo = parse_authors("LabAuthors.csv")

apapers = {}

for aauthor in ainfo:
    apapers[aauthor] = []

fh = open("papers.md")
for x in fh:
    if x[0] != '*': continue
    if x[1] == '*': continue
    thispaper = paper(x.strip())
#    if len(thispaper.doi) < 3:
#        print("Authors: {0}\nYear: {1}\nTitle: {2}\n URL: {3}\n Journal: {4}\n DOI: {5}\n".format(';'.join(thispaper.authors),thispaper.year,thispaper.title,thispaper.url,thispaper.journal,thispaper.doi))
    for aauthor in thispaper.authors:
        if aauthor in alookup:
            apapers[alookup[aauthor]].append(thispaper)

print(list(alookup))

for aauthor in apapers:
    if aauthor == 'James C. Schnable': continue
    apapers[aauthor].sort(key=lambda a:a.year)
    apapers[aauthor].reverse()
    mypage = open("../_includes/pub_lists/" + ainfo[aauthor]["filename"] + ".md",'w')
    mypage.write("<script type='text/javascript' src='https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js'></script><script async src=\"https://badge.dimensions.ai/badge.js\" charset=\"utf-8\"></script>")
    for apaper in apapers[aauthor]:
        mypage.write("<div data-badge-type=\"2\" data-doi=\"{0}\" data-hide-no-mentions=\"true\" data-hide-less-than=\"2\" class=\"altmetric-embed\" style=\"float:right;\"></div>\n".format(apaper.doi))
        mypage.write(apaper.citation + "\n")
    mypage.close()
