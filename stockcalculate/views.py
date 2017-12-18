from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import Http404
import sqlite3
import yaml
import csv

from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
import json
import requests


from datetime import datetime,timedelta
from pprint import pprint
from pymongo import MongoClient

def addStock(request):
	return render_to_response("stockcalculate/portfolio/oldindex.html")




def homepage(request):
	return render_to_response("index.html")



def portfolio(request):
	username=request.GET["username"]
	print username
	name=[]
	count=[]
	Client = MongoClient("localhost:27017")
	db = Client["operational_285"]
	userData = db.userdata.find({"username": username})
	print userData
	today_date=datetime.today().strftime('%Y-%m-%d')
	date_N_days_ago = datetime.now() - timedelta(days=10)
	old_date= date_N_days_ago.strftime('%Y-%m-%d')
	portDay1=0
	portDay2=0
	portDay3=0
	portDay4=0
	portDay5=0
	investedAm=0

	dayData=[]



	for allStockData in userData:
		for Stockname in allStockData["stocks"]:
			name.append(str(Stockname["name"]))
			count.append(Stockname["count"])
			url='https://www.quandl.com/api/v3/datasets/WIKI/'+str(Stockname["name"])+'.json?column_index=4&start_date='+str(old_date)+'&end_date='+str(today_date)+'&api_key=UerxA7FX2e_owB_Y5Esg'
			r = requests.get(url, stream=True)
			json_data=json.loads(r.text)
			day5_price=float(json_data["dataset"]["data"][4][1])
			day4_price=float(json_data["dataset"]["data"][3][1])
			day3_price=float(json_data["dataset"]["data"][2][1])
			day2_price=float(json_data["dataset"]["data"][1][1])
			day1_price=float(json_data["dataset"]["data"][0][1])
			count_current=int(Stockname["count"])
			investedAm+=count_current*int(Stockname["price"])
			portDay5+=count_current*day5_price
			portDay4+=count_current*day4_price
			portDay3+=count_current*day3_price
			portDay2+=count_current*day2_price
			portDay1+=count_current*day1_price


	dayData.append(int(portDay5))
	dayData.append(int(portDay4))
	dayData.append(int(portDay3))
	dayData.append(int(portDay2))
	dayData.append(int(portDay1))

	current_value=portDay1-investedAm
	print dayData

	strArr=[]
	username=request.GET["username"]
	with open('investment-strategy/strategy-stock.json') as data_file:
		data = json.load(data_file)

	print data["Investment Strategies"]



	return render_to_response("stockcalculate/portfolio/newport.html",{'data':data["Investment Strategies"],'username':username,'name':name,'count':count,'dayData':dayData,'investedAm':investedAm, 'current_value':current_value})


def marketHome(request):
	ethi_stock=[]
	ethi_num=[]

	grow_stock=[]
	grow_num=[]

	ind_stock=[]
	ind_num=[]

	qua_stock=[]
	qua_num=[]

	val_stock=[]
	val_num=[]


	with open('investment-strategy/strategy-stock.json') as data_file:
		data=yaml.safe_load(data_file)

		for element in data["Ethical Investing"]:
			ethi_stock.append(element["name"])
			ethi_num.append(str(element["portion"]))
		print ethi_stock
		print ethi_num

		for element in data["Growth Investing"]:
			grow_stock.append(str(element["name"]))
			grow_num.append(str(element["portion"]))
		print grow_stock
		print grow_num

		for element in data["Index Investing"]:
			ind_stock.append(str(element["name"]))
			ind_num.append(str(element["portion"]))
		print ind_stock
		print ind_num

		for element in data["Quality Investing"]:
			qua_stock.append(str(element["name"]))
			qua_num.append(str(element["portion"]))
		print qua_stock
		print qua_num

		for element in data["Value Investing"]:
			val_stock.append(str(element["name"]))
			val_num.append(str(element["portion"]))
		print val_stock
		print val_num


		appl_stock=[]
		appl_val=[]



		with open('investment-strategy/WIKI-AAPL.csv', 'rU') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',', quotechar='|',lineterminator='\r')
			for row in spamreader:
				appl_stock.append(row[0])
				appl_val.append(row[4])



	return render_to_response("stockcalculate/market/marketHome.html",{'ethi_stock':ethi_stock,'ethi_num':ethi_num,'grow_stock':grow_stock,'grow_num':grow_num,'ind_stock':ind_stock,
'ind_num':ind_num,'qua_stock':qua_stock,'qua_num':qua_num, 'val_stock':val_stock,'val_num':val_num,'appl_stock':appl_stock,'appl_val':appl_val})

def investHome(request):
	username=request.GET["username"]

	return render_to_response("stockcalculate/invest/investHome.html",{'username':username})

def trendHome(request):
	stockname=[]
	stockinvestment=[]
	strategyname=[]
	strategyinvestment=[]
	Client = MongoClient("localhost:27017")
	db = Client["analytical_285"]
	stockData = db.stockdata.find()
	strategyData = db.strategydata.find()
	for allStockData in stockData:
		stockname.append(str(allStockData["name"]))
		stockinvestment.append(allStockData["investment"])
	for allStrategyData in strategyData:
		strategyname.append(str(allStrategyData["name"]))
		strategyinvestment.append(allStrategyData["investment"])
	return render_to_response("stockcalculate/trend/trendHome.html",{'stockname':stockname,'stockinvestment':stockinvestment,'strategyname':strategyname,'strategyinvestment':strategyinvestment})




def investStrategy(request):
	strArr=[]
	username=request.GET["username"]
	with open('investment-strategy/strategy-stock.json') as data_file:
		data = json.load(data_file)

	print data["Investment Strategies"]

	return render_to_response("stockcalculate/invest/investStrategy.html",{'data':data["Investment Strategies"],'username':username})



def investStock(request):
	username=request.GET["username"]
	return render_to_response("stockcalculate/invest/investStock.html",{'username':username})


@csrf_exempt
def addstrategy(request):
	client = MongoClient('localhost', 27017)

	username=request.GET["username"]
	amount=int(request.POST["amount"])
	print amount
	strategy=request.POST["strategy"]
	ethi_stock=[]
	ethi_num=[]

	grow_stock=[]
	grow_num=[]

	ind_stock=[]
	ind_num=[]

	qua_stock=[]
	qua_num=[]

	val_stock=[]
	val_num=[]


	with open('investment-strategy/strategy-stock.json') as data_file:
		data=yaml.safe_load(data_file)

		for element in data["Ethical Investing"]:
			ethi_stock.append(element["name"])
			ethi_num.append(str(element["portion"]))
		print ethi_stock
		print ethi_num

		for element in data["Growth Investing"]:
			grow_stock.append(str(element["name"]))
			grow_num.append(str(element["portion"]))
		print grow_stock
		print grow_num

		for element in data["Index Investing"]:
			ind_stock.append(str(element["name"]))
			ind_num.append(str(element["portion"]))
		print ind_stock
		print ind_num

		for element in data["Quality Investing"]:
			qua_stock.append(str(element["name"]))
			qua_num.append(str(element["portion"]))
		print qua_stock
		print qua_num

		for element in data["Value Investing"]:
			val_stock.append(str(element["name"]))
			val_num.append(str(element["portion"]))
		print val_stock
		print val_num

		print strategy

		if strategy=="Ethical Investing":
			print "why"
			for i in range(len(ethi_stock)):
				db = client.operational_285
				collection = db.userdata
				tamount=(int(amount)*int(ethi_num[i]))/100
				today_date=datetime.today().strftime('%Y-%m-%d')
				date_N_days_ago = datetime.now() - timedelta(days=3)
				old_date= date_N_days_ago.strftime('%Y-%m-%d')

				url='https://www.quandl.com/api/v3/datasets/WIKI/'+str(ethi_stock[i])+'.json?column_index=4&start_date='+str(old_date)+'&end_date='+str(today_date)+'&api_key=UerxA7FX2e_owB_Y5Esg'
				r = requests.get(url, stream=True)
				json_data=json.loads(r.text)
				today_price=int(json_data["dataset"]["data"][0][1])
				count=int(tamount/today_price)
				db.userdata.update({"username":username},{"$push":{"stocks":{"name":str(ethi_stock[i]),"count":count,"price":today_price}}})
				db=client.analytical_285
				collection1=db.stockdata
				collection2=db.strategydata
				search=db.stockdata.find({"name":str(ethi_stock[i])})
				x=False
				for abc in search:
					x=True
					print abc["name"]
					if str(abc["name"])==str(ethi_stock[i]):
						intialvalue=int(abc["investment"])
						tamount=intialvalue+tamount
						db.stockdata.update({"name":str(ethi_stock[i])},{"$set":{"investment":tamount}})
						print "test1"
				if not x:
					db.stockdata.insert({"name":str(ethi_stock[i]),"investment":tamount})
					print "test2"

			search=db.strategydata.find({"name":strategy})
			x=False
			print amount
			for abc in search:
				x=True
				print abc["name"]
				if str(abc["name"])==str(strategy):
					intialvalue=int(abc["investment"])
					print intialvalue
					amount=int(intialvalue)+int(amount)
					print amount
					db.strategydata.update({"name":"Ethical Investing"},{"$set":{"investment":amount}})
					print "hello1"
			if not x:
				db.strategydata.insert({"name":"Ethical Investing" ,"investment":amount})
				print "hello2"

		elif strategy=="Growth Investing":
			for i in range(len(grow_stock)):
				db = client.operational_285
				collection = db.userdata
				tamount=(int(amount)*int(grow_num[i]))/100
				today_date=datetime.today().strftime('%Y-%m-%d')
				date_N_days_ago = datetime.now() - timedelta(days=3)
				old_date= date_N_days_ago.strftime('%Y-%m-%d')
				print old_date
				print today_date
				print grow_stock[i]

				url='https://www.quandl.com/api/v3/datasets/WIKI/'+str(grow_stock[i])+'.json?column_index=4&start_date='+str(old_date)+'&end_date='+str(today_date)+'&api_key=UerxA7FX2e_owB_Y5Esg'
				#https://www.quandl.com/api/v3/datasets/WIKI/EBAY.json?column_index=4&start_date=2017-12-14&end_date=2017-12-17&api_key=UerxA7FX2e_owB_Y5Esg
				r = requests.get(url, stream=True)
				json_data=json.loads(r.text)
				today_price=int(json_data["dataset"]["data"][0][1])
				count=int(tamount/today_price)
				db.userdata.update({"username":username},{"$push":{"stocks":{"name":str(grow_stock[i]),"count":count,"price":today_price}}})
				db=client.analytical_285
				collection1=db.stockdata
				collection2=db.strategydata
				search=db.stockdata.find({"name":str(grow_stock[i])})
				x=False
				for abc in search:
					x=True
					print abc["name"]
					if str(abc["name"])==str(grow_stock[i]):
						intialvalue=int(abc["investment"])
						tamount=intialvalue+tamount
						db.stockdata.update({"name":str(grow_stock[i])},{"$set":{"investment":tamount}})
						print "test1"
				if not x:
					db.stockdata.insert({"name":str(grow_stock[i]),"investment":tamount})
					print "test2"

			search=db.strategydata.find({"name":strategy})
			x=False
			print amount
			for abc in search:
				x=True
				print abc["name"]
				if str(abc["name"])==str(strategy):
					intialvalue=int(abc["investment"])
					print intialvalue
					amount=int(intialvalue)+int(amount)
					print amount
					db.strategydata.update({"name":"Growth Investing"},{"$set":{"investment":amount}})
					print "hello1"
			if not x:
				db.strategydata.insert({"name":"Growth Investing" ,"investment":amount})
				print "hello2"
			# grow_stock=[]
			# grow_num=[]


		elif strategy=="Index Investing":
			for i in range(len(ind_stock)):
				db = client.operational_285
				collection = db.userdata
				tamount=(int(amount)*int(ind_num[i]))/100
				today_date=datetime.today().strftime('%Y-%m-%d')
				date_N_days_ago = datetime.now() - timedelta(days=3)
				old_date= date_N_days_ago.strftime('%Y-%m-%d')
				print old_date
				print today_date
				print ind_stock[i]

				url='https://www.quandl.com/api/v3/datasets/WIKI/'+str(ind_stock[i])+'.json?column_index=4&start_date='+str(old_date)+'&end_date='+str(today_date)+'&api_key=UerxA7FX2e_owB_Y5Esg'
				#https://www.quandl.com/api/v3/datasets/WIKI/EBAY.json?column_index=4&start_date=2017-12-14&end_date=2017-12-17&api_key=UerxA7FX2e_owB_Y5Esg
				r = requests.get(url, stream=True)
				json_data=json.loads(r.text)
				today_price=int(json_data["dataset"]["data"][0][1])
				count=int(tamount/today_price)
				db.userdata.update({"username":username},{"$push":{"stocks":{"name":str(ind_stock[i]),"count":count,"price":today_price}}})
				db=client.analytical_285
				collection1=db.stockdata
				collection2=db.strategydata
				search=db.stockdata.find({"name":str(ind_stock[i])})
				x=False
				for abc in search:
					x=True
					print abc["name"]
					if str(abc["name"])==str(ind_stock[i]):
						intialvalue=int(abc["investment"])
						tamount=intialvalue+tamount
						db.stockdata.update({"name":str(ind_stock[i])},{"$set":{"investment":tamount}})
						print "test1"
				if not x:
					db.stockdata.insert({"name":str(ind_stock[i]),"investment":tamount})
					print "test2"

			search=db.strategydata.find({"name":strategy})
			x=False
			print amount
			for abc in search:
				x=True
				print abc["name"]
				if str(abc["name"])==str(strategy):
					intialvalue=int(abc["investment"])
					print intialvalue
					amount=int(intialvalue)+int(amount)
					print amount
					db.strategydata.update({"name":"Index Investing"},{"$set":{"investment":amount}})
					print "hello1"
			if not x:
				db.strategydata.insert({"name":"Index Investing" ,"investment":amount})
				print "hello2"
			#ind_stock=[]
			#ind_num=[]


		elif strategy=="Quality Investing":
			for i in range(len(qua_stock)):
				db = client.operational_285
				collection = db.userdata
				tamount=(int(amount)*int(qua_num[i]))/100
				today_date=datetime.today().strftime('%Y-%m-%d')
				date_N_days_ago = datetime.now() - timedelta(days=3)
				old_date= date_N_days_ago.strftime('%Y-%m-%d')
				print old_date
				print today_date
				print qua_stock[i]

				url='https://www.quandl.com/api/v3/datasets/WIKI/'+str(qua_stock[i])+'.json?column_index=4&start_date='+str(old_date)+'&end_date='+str(today_date)+'&api_key=UerxA7FX2e_owB_Y5Esg'
				#https://www.quandl.com/api/v3/datasets/WIKI/EBAY.json?column_index=4&start_date=2017-12-14&end_date=2017-12-17&api_key=UerxA7FX2e_owB_Y5Esg
				r = requests.get(url, stream=True)
				json_data=json.loads(r.text)
				today_price=int(json_data["dataset"]["data"][0][1])
				count=int(tamount/today_price)
				db.userdata.update({"username":username},{"$push":{"stocks":{"name":str(qua_stock[i]),"count":count,"price":today_price}}})
				db=client.analytical_285
				collection1=db.stockdata
				collection2=db.strategydata
				search=db.stockdata.find({"name":str(qua_stock[i])})
				x=False
				for abc in search:
					x=True
					print abc["name"]
					if str(abc["name"])==str(qua_stock[i]):
						intialvalue=int(abc["investment"])
						tamount=intialvalue+tamount
						db.stockdata.update({"name":str(qua_stock[i])},{"$set":{"investment":tamount}})
						print "test1"
				if not x:
					db.stockdata.insert({"name":str(qua_stock[i]),"investment":tamount})
					print "test2"

			search=db.strategydata.find({"name":strategy})
			x=False
			print amount
			for abc in search:
				x=True
				print abc["name"]
				if str(abc["name"])==str(strategy):
					intialvalue=int(abc["investment"])
					print intialvalue
					amount=int(intialvalue)+int(amount)
					print amount
					db.strategydata.update({"name":"Quality Investing"},{"$set":{"investment":amount}})
					print "hello1"
			if not x:
				db.strategydata.insert({"name":"Quality Investing" ,"investment":amount})
				print "hello2"
			#qua_stock=[]
			#qua_num=[]

		elif strategy=="Value Investing":
			for i in range(len(val_stock)):
				db = client.operational_285
				collection = db.userdata
				tamount=(int(amount)*int(val_num[i]))/100
				today_date=datetime.today().strftime('%Y-%m-%d')
				date_N_days_ago = datetime.now() - timedelta(days=3)
				old_date= date_N_days_ago.strftime('%Y-%m-%d')
				print old_date
				print today_date
				print val_stock[i]

				url='https://www.quandl.com/api/v3/datasets/WIKI/'+str(val_stock[i])+'.json?column_index=4&start_date='+str(old_date)+'&end_date='+str(today_date)+'&api_key=UerxA7FX2e_owB_Y5Esg'
				#https://www.quandl.com/api/v3/datasets/WIKI/EBAY.json?column_index=4&start_date=2017-12-14&end_date=2017-12-17&api_key=UerxA7FX2e_owB_Y5Esg
				r = requests.get(url, stream=True)
				json_data=json.loads(r.text)
				today_price=int(json_data["dataset"]["data"][0][1])
				count=int(tamount/today_price)
				db.userdata.update({"username":username},{"$push":{"stocks":{"name":str(val_stock[i]),"count":count,"price":today_price}}})
				db=client.analytical_285
				collection1=db.stockdata
				collection2=db.strategydata
				search=db.stockdata.find({"name":str(val_stock[i])})
				x=False
				for abc in search:
					x=True
					print abc["name"]
					if str(abc["name"])==str(val_stock[i]):
						intialvalue=int(abc["investment"])
						tamount=intialvalue+tamount
						db.stockdata.update({"name":str(val_stock[i])},{"$set":{"investment":tamount}})
						print "test1"
				if not x:
					db.stockdata.insert({"name":str(val_stock[i]),"investment":tamount})
					print "test2"

			search=db.strategydata.find({"name":strategy})
			x=False
			print amount
			for abc in search:
				x=True
				print abc["name"]
				if str(abc["name"])==str(strategy):
					intialvalue=int(abc["investment"])
					print intialvalue
					amount=int(intialvalue)+int(amount)
					print amount
					db.strategydata.update({"name":"Value Investing"},{"$set":{"investment":amount}})
					print "hello1"
			if not x:
				db.strategydata.insert({"name":"Value Investing" ,"investment":amount})
				print "hello2"
			#val_stock=[]
			#val_num=[]
	username=request.GET["username"]
	print username
	name=[]
	count=[]
	Client = MongoClient("localhost:27017")
	db = Client["operational_285"]
	userData = db.userdata.find({"username": username})
	print userData
	today_date=datetime.today().strftime('%Y-%m-%d')
	date_N_days_ago = datetime.now() - timedelta(days=10)
	old_date= date_N_days_ago.strftime('%Y-%m-%d')
	portDay1=0
	portDay2=0
	portDay3=0
	portDay4=0
	portDay5=0
	investedAm=0

	dayData=[]



	for allStockData in userData:
		for Stockname in allStockData["stocks"]:
			name.append(str(Stockname["name"]))
			count.append(Stockname["count"])
			url='https://www.quandl.com/api/v3/datasets/WIKI/'+str(Stockname["name"])+'.json?column_index=4&start_date='+str(old_date)+'&end_date='+str(today_date)+'&api_key=UerxA7FX2e_owB_Y5Esg'
			r = requests.get(url, stream=True)
			json_data=json.loads(r.text)
			day5_price=float(json_data["dataset"]["data"][4][1])
			day4_price=float(json_data["dataset"]["data"][3][1])
			day3_price=float(json_data["dataset"]["data"][2][1])
			day2_price=float(json_data["dataset"]["data"][1][1])
			day1_price=float(json_data["dataset"]["data"][0][1])
			count_current=int(Stockname["count"])
			investedAm+=count_current*int(Stockname["price"])
			portDay5+=count_current*day5_price
			portDay4+=count_current*day4_price
			portDay3+=count_current*day3_price
			portDay2+=count_current*day2_price
			portDay1+=count_current*day1_price


	dayData.append(int(portDay5))
	dayData.append(int(portDay4))
	dayData.append(int(portDay3))
	dayData.append(int(portDay2))
	dayData.append(int(portDay1))

	current_value=portDay1-investedAm
	print dayData

	strArr=[]
	username=request.GET["username"]
	with open('investment-strategy/strategy-stock.json') as data_file:
		data = json.load(data_file)

	print data["Investment Strategies"]



	return render_to_response("stockcalculate/portfolio/newport.html",{'data':data["Investment Strategies"],'username':username,'name':name,'count':count,'dayData':dayData,'investedAm':investedAm, 'current_value':current_value})


#	return render_to_response("stockcalculate/addedStrategy.html",{'username':username})


@csrf_exempt
def addData(request):
	username=request.GET["username"]
	client = MongoClient('localhost', 27017)
	db = client.operational_285
	collection = db.userdata
	total_investment= float(request.POST['amount'])
	stockname= request.POST['name']
	today_date=datetime.today().strftime('%Y-%m-%d')
	date_N_days_ago = datetime.now() - timedelta(days=3)
	old_date= date_N_days_ago.strftime('%Y-%m-%d')

	url='https://www.quandl.com/api/v3/datasets/WIKI/'+str(stockname)+'.json?column_index=4&start_date='+str(old_date)+'&end_date='+str(today_date)+'&api_key=UerxA7FX2e_owB_Y5Esg'
	r = requests.get(url, stream=True)
	json_data=json.loads(r.text)
	today_price=float(json_data["dataset"]["data"][0][1])
	count=int(total_investment/today_price)
	db.userdata.update({"username":username},{"$push":{"stocks":{"name":stockname,"count":count,"price":today_price}}})
	db=client.analytical_285
	collection1=db.stockdata
	collection2=db.strategydata
	search=db.stockdata.find({"name":stockname})
	x=False
	for abc in search:
		x=True
		print abc["name"]
		if str(abc["name"])==stockname:
			intialvalue=abc["investment"]
			total_investment=intialvalue+total_investment
			db.stockdata.update({"name":stockname},{"$set":{"investment":total_investment}})
			print "test1"
	if not x:
		db.stockdata.insert({"name":stockname,"investment":total_investment})
		print "test2"

	return render_to_response("stockcalculate/addedStocks.html",{'username':username})


@csrf_exempt
def getValue(request):
	client = MongoClient('localhost', 27017)
	db = client.operational_285
	collection = db.userdata
	username=request.GET["username"]
		# username=request.GET["username"]
	stock_symbol= str(request.POST['ticker_symbol'])
	allotment= int(request.POST['allotment'])
	initial_share_price=float(request.POST['buying_share_price'])
	total_investment=allotment*initial_share_price
	if float(allotment) <0:
		raise Exception('Error:', 'Allotment has to be positive')
	if float(initial_share_price) <0:
		raise Exception('Error:', 'Initial Share Price should not be negative')
	data=collection.find_one({"username":username})
	db.userdata.update({"username":username},{"$push":{"stocks":{"name":stock_symbol,"count":allotment,"price":initial_share_price}}})
	db=client.analytical_285
	collection1=db.stockdata
	collection2=db.strategydata

	search=db.stockdata.find({"name":stock_symbol})
	x=False
	for abc in search:
		x=True
		if str(abc["name"])==stock_symbol:
			intialvalue=int(abc["investment"])
			total_investment=intialvalue+total_investment
			db.stockdata.update({"name":stock_symbol},{"$set":{"investment":total_investment}})
	if not x:
		db.stockdata.insert({"name":stock_symbol,"investment":total_investment})


	return render_to_response("stockcalculate/profitReport.html",{'username':username})

@csrf_exempt
def login(request):
	connection = sqlite3.connect('login.db')
	cursor=connection.cursor()
	login_user_name=request.GET['username']
	login_user_password=request.GET['loginpassword']
	cursor.execute('SELECT Username from login where Username = ?',(login_user_name,))
	try:
		usr=cursor.fetchall()[0][0]
	except Exception as inst:
		return render_to_response("stockcalculate/failure.html")

	if (login_user_name==usr):
		cursor.execute('SELECT Password from login where Username = ?',(login_user_name,))
		pwd=cursor.fetchall()[0][0]
		if (login_user_password==pwd):
			username=request.GET["username"]
			print username
			name=[]
			count=[]
			Client = MongoClient("localhost:27017")
			db = Client["operational_285"]
			userData = db.userdata.find({"username": username})
			print userData
			today_date=datetime.today().strftime('%Y-%m-%d')
			date_N_days_ago = datetime.now() - timedelta(days=10)
			old_date= date_N_days_ago.strftime('%Y-%m-%d')
			portDay1=0
			portDay2=0
			portDay3=0
			portDay4=0
			portDay5=0
			investedAm=0

			dayData=[]



			for allStockData in userData:
				for Stockname in allStockData["stocks"]:
					name.append(str(Stockname["name"]))
					count.append(Stockname["count"])
					url='https://www.quandl.com/api/v3/datasets/WIKI/'+str(Stockname["name"])+'.json?column_index=4&start_date='+str(old_date)+'&end_date='+str(today_date)+'&api_key=UerxA7FX2e_owB_Y5Esg'
					r = requests.get(url, stream=True)
					json_data=json.loads(r.text)
					day5_price=float(json_data["dataset"]["data"][4][1])
					day4_price=float(json_data["dataset"]["data"][3][1])
					day3_price=float(json_data["dataset"]["data"][2][1])
					day2_price=float(json_data["dataset"]["data"][1][1])
					day1_price=float(json_data["dataset"]["data"][0][1])
					count_current=int(Stockname["count"])
					investedAm+=count_current*int(Stockname["price"])
					portDay5+=count_current*day5_price
					portDay4+=count_current*day4_price
					portDay3+=count_current*day3_price
					portDay2+=count_current*day2_price
					portDay1+=count_current*day1_price


			dayData.append(int(portDay5))
			dayData.append(int(portDay4))
			dayData.append(int(portDay3))
			dayData.append(int(portDay2))
			dayData.append(int(portDay1))

			current_value=portDay1-investedAm
			print dayData

			strArr=[]
			username=request.GET["username"]
			with open('investment-strategy/strategy-stock.json') as data_file:
				data = json.load(data_file)
			print data["Investment Strategies"]
			return render_to_response("stockcalculate/portfolio/newport.html",{'data':data["Investment Strategies"],'username':username,'name':name,'count':count,'dayData':dayData,'investedAm':investedAm, 'current_value':current_value})

		elif (login_user_password!=pwd):
			return render_to_response("stockcalculate/failure.html")
		# print usr
	elif (login_user_name!=usr):
		return render_to_response("stockcalculate/failure.html")

def register(request):
	client = MongoClient('localhost', 27017)
	db = client.operational_285
	collection = db.userdata
	connection = sqlite3.connect('login.db')
	cursor=connection.cursor()
	user_name=request.GET['name']
	user_email=request.GET['email']
	user_password=request.GET['password']
	user_repassword=request.GET['password1']
	print user_repassword
	try:
		if (user_password==user_repassword):
			cursor.execute('''INSERT INTO login(Username,Email,Password) values(?,?,?)''', (user_name,user_email,user_password))
			result = db.userdata.insert_one({"username":user_name,"stocks":[]})
			connection.commit()
			connection.close()
			return render_to_response("stockcalculate/signup.html")
	except Exception as exp:
		return render_to_response("stockcalculate/passwordmatch.html")
	else:
		return render_to_response("stockcalculate/passwordmatch.html")


def forgot(request):
	return render_to_response("stockcalculate/forgot.html")

def change(request):
	connection = sqlite3.connect('login.db')
	cursor=connection.cursor()
	in_name=request.GET['inname']
	in_email=request.GET['inemail']
	user_pass1=request.GET['password1']
	user_pass2=request.GET['password2']
	cursor.execute('SELECT Username from login where Username = ?',(in_name,))
	try:
		user1=cursor.fetchall()[0][0]
	except Exception as inst:
		return render_to_response("stockcalculate/invaliduser.html")
	if (in_name==user1):
		cursor.execute('SELECT Email from login where Username = ?',(in_name,))
		eml=cursor.fetchall()[0][0]
		if(in_email!=eml):
			return render_to_response("stockcalculate/invalidemail.html")
		elif (in_email==eml and user_pass1==user_pass2):
			cursor.execute("""UPDATE login SET Password = ? WHERE Username= ? """,(user_pass1,in_name,))
			connection.commit()
			connection.close()
			return render_to_response("stockcalculate/index.html")
		else:
			return render_to_response("stockcalculate/passwordmatch.html")

def getComma(f):
    s = str(abs(f))
    decimalposition = s.find(".")
    if decimalposition == -1:
        decimalposition = len(s)
    comma_to_number = ""
    for i in range(decimalposition+1, len(s)):
        if not (i-decimalposition-1) % 3 and i-decimalposition-1: comma_to_number = comma_to_number+","
        comma_to_number = comma_to_number+s[i]
    if len(comma_to_number):
        comma_to_number = "."+comma_to_number
    for i in range(decimalposition-1,-1,-1):
        if not (decimalposition-i-1) % 3 and decimalposition-i-1: comma_to_number = ","+comma_to_number
        comma_to_number = s[i]+comma_to_number
    if f < 0:
        comma_to_number = "-"+comma_to_number
    return comma_to_number
