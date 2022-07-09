from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import re

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find(class_ = 'lister-list')
row = table.find_all(class_ = 'lister-item mode-advanced')

row_length = len(row)

temp = [] #initiating a tuple

for i in range(0, row_length):

    title = table.find_all(class_ = 'lister-item-header')[i]
    title = title.find(href=re.compile ('title')).text
    rating = table.find_all(class_ = 'inline-block ratings-imdb-rating')[i]
    rating = rating.find('strong').text
    metascore = table.find_all(class_ = 'ratings-bar')[i]
    metascore = metascore.find(class_ = 'inline-block ratings-metascore')
    if metascore == None:
        metascore = 0
    else:
        metascore = metascore.find('span').text.strip()
    votes = table.find_all(class_ = 'sort-num_votes-visible')[i]
    votes = votes.find_all('span')[1].text
    votes = votes.replace(',','')
    
    temp.append((title, rating, metascore, votes))

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('Title', 'Ratings', 'Metascore', 'Votes'))

#insert data wrangling here
df['Ratings'] = df['Ratings'].astype('float')
df[['Metascore', 'Votes']] = df[['Metascore', 'Votes']].astype('int64')
df = df.set_index('Title')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Ratings"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df['Ratings'].sort_values(ascending = False).head(7).plot.bar(rot = 0, figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

    # generate plot
	ay = df['Votes'].sort_values(ascending = False).head(7).plot.bar(rot = 0, figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile2 = BytesIO()
	plt.savefig(figfile2, format='png', transparent=True)
	figfile2.seek(0)
	figdata_png2 = base64.b64encode(figfile2.getvalue())
	plot_result2 = str(figdata_png2)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
        plot_result2=plot_result2
		)


if __name__ == "__main__": 
    app.run(debug=True)