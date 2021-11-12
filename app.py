from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div',{'class':'lister list detail sub-list'})
row = table.find_all('div',attrs={'class':'lister-item mode-advanced'})

row_length = len('row')

temp = [] #initiating a list 

for item in row:

    title = item.find_all('h3',attrs={'class':'lister-item-header'})[0].text[3:]
    title = title.replace('\n','').replace('(2021)','').replace('(2021– )','').replace('.','')
    
    try:
    #get volume
        imdb = item.find_all('div',attrs={'class' : 'inline-block ratings-imdb-rating'})[0].text
        imdb = imdb.replace('\n','')
    except:
        imdb ='0.0'
        
    try:
        metascore = item.find_all('div',attrs={'class' : 'ratings-metascore'})[0].text
        metascore = metascore.replace('\n','').replace('Metascore','').replace('                            ','')
    except:
        metascore = '0'
    
    try:
    #scrapping process, menampilkan text yang ada di website
        votes = item.find_all('span',attrs={'name':'nv'})[0].text
        votes = votes.replace(',','')
    except:
        votes = '0'
        
    temp.append((title,imdb,metascore,votes))    
temp
#change into dataframe
df = pd.DataFrame(temp, columns = ('title','metascore','imdb','votes'))

#insert data wrangling here
df['imdb'] = df['imdb'].astype('int')
df['metascore'] = df['metascore'].astype('float')
df['votes'] = df['votes'].astype('int')
df=df.set_index('title')
df.dtypes

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["metascore"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	df.iloc[:,0:1].sort_values('metascore', ascending=False).iloc[0:7,:].plot.bar(figsize = (11,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)