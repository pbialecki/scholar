import requests
import bs4
import re
import sys
import codecs
import sqlite3 as lite
import time
import random

if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
first = [line.strip() for line in open('first.txt')]
second = [line.strip() for line in open('second.txt')]

try:
    con = lite.connect('db.db3')     
    with con:
        cur = con.cursor()    
        cur.execute("DROP TABLE IF EXISTS Publications")
        cur.execute("CREATE TABLE Publications(Id INTEGER PRIMARY KEY, Query TEXT, ResultNo TEXT, Title TEXT, Authors TEXT, Date TEXT, Source TEXT, Citations TEXT)")
        con.commit() 
except lite.Error as e:
    if con:
        con.rollback()                
    print("SQLiteError %s:" % e.args[0])    
finally:            
    if con:
        con.close()  

for f in first:
    for s in second:
        for page in range(0, 3):
            query = f + '+' + s
        #     query="graph model".replace(" ","+")
            response = requests.get('http://scholar.google.pl/scholar?start=' + str(page) + '0&q=' + query + '&hl=pl&as_sdt=0,5')
            soup = bs4.BeautifulSoup(response.text)
            time.sleep(40 + random.randint(1, 20))
            titles = soup.findAll("h3", { "class" : "gs_rt" })
            authors = soup.findAll("div", { "class" : "gs_a" })
            links = [div.find('a') for div in soup.findAll("div", { "class" : "gs_fl" })]
         
            p = re.compile('Cytowane przez')
            citations = []
            for elem in links:
                if p.search(elem.text):
                    citations.append(elem.text.split(" ")[2])
            resultNo = '0'
            
            print(response.text)
            
            for item in range(0, 10):
                if (titles[item] is not None) and (authors[item] is not None) and (citations[item] is not None):
                    if(page == 0):
                        resultNo = str(item)
                    else:
                        resultNo = str(page) + str(item)
                         
                    title = re.sub('\[.+\]', '', titles[item].text).strip()        
                    author = authors[item].text       
#                     date = authors[item].text.split(" - ")[1]
#                     source = authors[item].text.split(" - ")[2]    
                    citation = citations[item]
         
                    print(query.replace("+", " "))
                    print(resultNo)
                    print(title)
                    print(author)
#                     print(date)
#                     print(source)
                    print(citation)
                    print()
                    try:
                        con = lite.connect('db.db3')
                         
                        with con:
                            cur = con.cursor()
                        cur.execute("INSERT INTO Publications(Query,ResultNo,Title,Authors,Date,Source,Citations) VALUES(?,?,?,?,?,?,?)", (query.replace("+", " "), resultNo, title, author.strip(), "", "", citation))
                        con.commit() 
                    except lite.Error as e:
                        if con:
                            con.rollback()                
                        print("SQLiteError %s:" % e.args[0])    
                    finally:            
                        if con:
                            con.close()  
