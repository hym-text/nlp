# -*- coding: utf-8 -*
import xml.etree.ElementTree as ET
import mysql.connector
import matplotlib.pyplot as plt
import os
import MeCab
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from lxml import etree

#mecab用のパーサー
m = MeCab.Tagger ("-Owakati")

#xml用のパーサー
parser = etree.XMLParser(recover=True)

#MySQLに接続するための準備
conn = mysql.connector.connect(user='root', password='root', host='localhost', database='ja2',charset="utf8")
cur = conn.cursor()
cur.execute("select *  from categorylinks where cl_to like 'アニメ';")
ani_list=[]

#結果から0列目の要素のみをリストに追加する
for row in cur.fetchall():
    ani_list.append(row[0])    

cur.close
conn.close

#liは集めるべき記事IDのリスト
ani_list.sort()
li=list(set(ani_list))
li.sort()


#学習用文書データのリスト
training_docs = []

#ディレクトリ指定
directory = os.listdir('./extracted')

#AA-ZZにソートする
directory.sort()

step=0

#タグ付き文書のリスト
sent=[]

f2=open("anidata.txt","w")
for i in range(len(directory)):
    directory2 = os.listdir('./extracted/'+directory[i])
    directory2.sort()
    for i2 in range(len(directory2)):
        f=open('./extracted/'+directory[i]+"/"+directory2[i2])
        d=f.read()
        #無理やり木構造にして読み込み
        tree = ET.fromstring("<window>"+d+"</window>",parser=parser)
        for e in tree:
            d=e.get('id')
            if e.get('id')==None:
               d="0"
            if int(d)==int(li[step]):
                f2.write(m.parse (e.text))
                sent.append(TaggedDocument(words=(m.parse (e.text)).split(" "),
                       tags=[e.get('title')]))
                step=step+1
            elif (int(d)>int(li[step])):
                step=step+1
            if step>len(li)-1:
                
                for i in range(len(sent)):
                    training_docs.append(sent[i])
                model = Doc2Vec(documents=training_docs, min_count=1, dm=0)
                model.save('doc2vec.model')
                exit(1)
