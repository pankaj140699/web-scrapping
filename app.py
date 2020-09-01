
from bs4 import BeautifulSoup as soup
import urllib
import requests
import pandas as pd
import time
import os
from flask import Flask, render_template,  session, redirect, request
from flask_cors import CORS,cross_origin
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# define global paths for Image and csv folders
IMG_FOLDER = os.path.join('static', 'images')
CSV_FOLDER = os.path.join('static', 'CSVs')

app = Flask(__name__)
# config environment variables
app.config['IMG_FOLDER'] = IMG_FOLDER
app.config['CSV_FOLDER'] = CSV_FOLDER

class DataCollection:
	'''
	class meant for collection and management of data
	'''
	def __init__(self):
		# dictionary to gather data
		self.data = {"Name": list(), 
		"Position": list()}

	def get_final_data(self, name=None,position=None):
		'''
		this will append data gathered from comment box into data dictionary
		'''
		# append product name
		for i in range(len(name)):
			self.data["Name"].append(name[i])
		for i in range(len(position)):
			self.data["Position"].append(position[i])

	def get_main_HTML(self, base_URL=None):
		'''
		return main html page based on search string
		'''
		# construct the search url with base URL and search string
		search_url = f"{base_URL}"
		# usung urllib read the page
		with urllib.request.urlopen(search_url) as url:
			page = url.read()
		# return the html page after parsing with bs4
		return soup(page, "html.parser")

	def get_product_name(self, flipkart_base=None, bigBoxes=None):
		'''
		returns list of (product name, product link)
		'''
		# temporary list to return the results
		temp = []
		# iterate over list of bigBoxes
		for box in bigBoxes:
			try:
				# if prod name and list present then append them in temp
				temp.append((box.span.get_text()))
			except:
				pass
			
		return temp
	def get_position(self, flipkart_base=None, bigBoxes=None):
		'''
		returns list of (product name, product link)
		'''
		# temporary list to return the results
		temp = []
		# iterate over list of bigBoxes
		for box in bigBoxes:
			try:
				# if prod name and list present then append them in temp
				temp.append((box.div.div.ul.li.text))
			except:
				pass
			
		return temp

	def get_data_dict(self):
		'''
		returns collected data in dictionary
		'''
		return self.data

	def save_as_dataframe(self, dataframe, fileName=None):
		'''
		it saves the dictionary dataframe as csv by given filename inside
		the CSVs folder and returns the final path of saved csv
		'''
		# save the CSV file to CSVs folder
		csv_path = os.path.join(app.config['CSV_FOLDER'], fileName)
		fileExtension = '.csv'
		final_path = f"{csv_path}{fileExtension}"
		# clean previous files -
		CleanCache(directory=app.config['CSV_FOLDER'])
		# save new csv to the csv folder
		dataframe.to_csv(final_path, index=None)
		print("File saved successfully!!")
		return final_path


class CleanCache:
	'''
	this class is responsible to clear any residual csv and image files
	present due to the past searches made.
	'''
	def __init__(self, directory=None):
		self.clean_path = directory
		# only proceed if directory is not empty
		if os.listdir(self.clean_path) != list():
			# iterate over the files and remove each file
			files = os.listdir(self.clean_path)
			for fileName in files:
				print(fileName)
				os.remove(os.path.join(self.clean_path,fileName))
		print("cleaned!")

# route to display the home page
@app.route('/',methods=['GET'])  
@cross_origin()
def homePage():
	return render_template("index.html")

# route to display the review page
@app.route('/review', methods=("POST", "GET"))
@cross_origin()
def index():
	if request.method == 'POST':
		try:
			# get base URL and a search string to query the website
			base_URL = 'https://www.india.gov.in/my-government/whos-who/council-ministers' # 'https://www.' + input("enter base URL: ")
			search_string = request.form['content']
			# print('processing...') 

			# start counter to count time in seconds
			start = time.perf_counter()

			get_data = DataCollection()

			# store main HTML page for given search query
			flipkart_HTML = get_data.get_main_HTML(base_URL)

			# store all the boxes containing products
			bigBoxes1 = flipkart_HTML.find_all('div',class_="views-field-title")
			bigBoxes2 = flipkart_HTML.find_all('div',class_="views-field-field-ministries")
			
			# store extracted product name links
			product_name = get_data.get_product_name(base_URL, bigBoxes1)
			position= get_data.get_position(base_URL, bigBoxes2)
			# title1= get_data.get_position(base_URL, bigBoxes3) 
			# print(position)
			# iterate over product name and links list
			# prpare final data
			get_data.get_final_data(product_name, position)

			# save the data as gathered in dataframe
			df = pd.DataFrame(get_data.get_data_dict())
			df1=pd.read_csv('static\\CSVs\\india.csv',index_col='Name')
			# print(df)
			# print(df1)
			# print(df1.loc[search_string,"Position"])
			# save dataframe as a csv which will be availble to download
			download_path = get_data.save_as_dataframe(df, fileName='india')
			df2=df1.loc[search_string,"Position"]
			# finish time counter and calclulate time taked to complet ethis programe
			finish = time.perf_counter()
			# tables=[df.to_html(classes='data')]
			# print(df[search_string])
			# df1=pd.read_csv('',ind)
			# print(f"program finished with and timelapsed: {finish - start} second(s)") 
			return render_template('review.html',
			search_string=search_string, 
			datavalue=[df2]# pass the df as html 
			# download_csv=download_path # pass the download path for csv
			)
		except Exception as e:
			print(e)
			# return 404 page if error occurs 
			return render_template("404.html")

	else:
		# return index page if home is pressed or for the first run
		return render_template("index.html")

if __name__ == '__main__':
	app.run()