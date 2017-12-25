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



def homepage(request):
	return render_to_response("index.html")

def portfolio(request):
	username=request.GET["username"]
	name=[]
	count=[]
	Client = MongoClient("localhost:27017")
	db = Client["operational_285"]
	userData = db.userdata.find({"username": username})
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

	strArr=[]
	username=request.GET["username"]
	with open('investment-strategy/strategy-stock.json') as data_file:
		data = json.load(data_file)




	return render_to_response("stockcalculate/portfolio/newport.html",{'data':data["Investment Strategies"],'username':username,'name':name,'count':count,'dayData':dayData,'investedAm':investedAm, 'current_value':current_value})


@csrf_exempt
def addstrategy(request):
	client = MongoClient('localhost', 27017)

	username=request.GET["username"]
	amount=int(request.POST["amount"])
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

		for element in data["Growth Investing"]:
			grow_stock.append(str(element["name"]))
			grow_num.append(str(element["portion"]))


		for element in data["Index Investing"]:
			ind_stock.append(str(element["name"]))
			ind_num.append(str(element["portion"]))


		for element in data["Quality Investing"]:
			qua_stock.append(str(element["name"]))
			qua_num.append(str(element["portion"]))


		for element in data["Value Investing"]:
			val_stock.append(str(element["name"]))
			val_num.append(str(element["portion"]))



		if strategy=="Ethical Investing":
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
					if str(abc["name"])==str(ethi_stock[i]):
						intialvalue=int(abc["investment"])
						tamount=intialvalue+tamount
						db.stockdata.update({"name":str(ethi_stock[i])},{"$set":{"investment":tamount}})
				if not x:
					db.stockdata.insert({"name":str(ethi_stock[i]),"investment":tamount})

			search=db.strategydata.find({"name":strategy})
			x=False
			for abc in search:
				x=True
				if str(abc["name"])==str(strategy):
					intialvalue=int(abc["investment"])
					amount=int(intialvalue)+int(amount)
					db.strategydata.update({"name":"Ethical Investing"},{"$set":{"investment":amount}})
			if not x:
				db.strategydata.insert({"name":"Ethical Investing" ,"investment":amount})

		elif strategy=="Growth Investing":
			for i in range(len(grow_stock)):
				db = client.operational_285
				collection = db.userdata
				tamount=(int(amount)*int(grow_num[i]))/100
				today_date=datetime.today().strftime('%Y-%m-%d')
				date_N_days_ago = datetime.now() - timedelta(days=3)
				old_date= date_N_days_ago.strftime('%Y-%m-%d')

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
					if str(abc["name"])==str(grow_stock[i]):
						intialvalue=int(abc["investment"])
						tamount=intialvalue+tamount
						db.stockdata.update({"name":str(grow_stock[i])},{"$set":{"investment":tamount}})
				if not x:
					db.stockdata.insert({"name":str(grow_stock[i]),"investment":tamount})

			search=db.strategydata.find({"name":strategy})
			x=False
			for abc in search:
				x=True
				if str(abc["name"])==str(strategy):
					intialvalue=int(abc["investment"])
					amount=int(intialvalue)+int(amount)
					db.strategydata.update({"name":"Growth Investing"},{"$set":{"investment":amount}})
			if not x:
				db.strategydata.insert({"name":"Growth Investing" ,"investment":amount})
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
					if str(abc["name"])==str(ind_stock[i]):
						intialvalue=int(abc["investment"])
						tamount=intialvalue+tamount
						db.stockdata.update({"name":str(ind_stock[i])},{"$set":{"investment":tamount}})
				if not x:
					db.stockdata.insert({"name":str(ind_stock[i]),"investment":tamount})

			search=db.strategydata.find({"name":strategy})
			x=False
			for abc in search:
				x=True
				if str(abc["name"])==str(strategy):
					intialvalue=int(abc["investment"])
					amount=int(intialvalue)+int(amount)
					db.strategydata.update({"name":"Index Investing"},{"$set":{"investment":amount}})
			if not x:
				db.strategydata.insert({"name":"Index Investing" ,"investment":amount})
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
					if str(abc["name"])==str(qua_stock[i]):
						intialvalue=int(abc["investment"])
						tamount=intialvalue+tamount
						db.stockdata.update({"name":str(qua_stock[i])},{"$set":{"investment":tamount}})
				if not x:
					db.stockdata.insert({"name":str(qua_stock[i]),"investment":tamount})

			search=db.strategydata.find({"name":strategy})
			x=False
			for abc in search:
				x=True
				if str(abc["name"])==str(strategy):
					intialvalue=int(abc["investment"])
					amount=int(intialvalue)+int(amount)
					db.strategydata.update({"name":"Quality Investing"},{"$set":{"investment":amount}})
			if not x:
				db.strategydata.insert({"name":"Quality Investing" ,"investment":amount})
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
					if str(abc["name"])==str(val_stock[i]):
						intialvalue=int(abc["investment"])
						tamount=intialvalue+tamount
						db.stockdata.update({"name":str(val_stock[i])},{"$set":{"investment":tamount}})
				if not x:
					db.stockdata.insert({"name":str(val_stock[i]),"investment":tamount})

			search=db.strategydata.find({"name":strategy})
			x=False
			for abc in search:
				x=True
				if str(abc["name"])==str(strategy):
					intialvalue=int(abc["investment"])
					amount=int(intialvalue)+int(amount)
					db.strategydata.update({"name":"Value Investing"},{"$set":{"investment":amount}})
			if not x:
				db.strategydata.insert({"name":"Value Investing" ,"investment":amount})
			#val_stock=[]
			#val_num=[]
	username=request.GET["username"]
	name=[]
	count=[]
	Client = MongoClient("localhost:27017")
	db = Client["operational_285"]
	userData = db.userdata.find({"username": username})
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

	strArr=[]
	username=request.GET["username"]
	with open('investment-strategy/strategy-stock.json') as data_file:
		data = json.load(data_file)

	stock_name = []
	stock_percent = []
	for i in data[strategy]:
		stock_percent.append(int(i['portion']))
		stock_name.append(str(i['name']))


	return render_to_response("stockcalculate/portfolio/newport.html",{'stock_name':stock_name,'stock_percent':stock_percent,'strategy':strategy,'data':data["Investment Strategies"],'username':username,'name':name,'count':count,'dayData':dayData,'investedAm':investedAm, 'current_value':current_value,'strategyset':True})


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
		return render_to_response("index.html",{'anchor':True})

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
			return render_to_response("index.html",{'anchor':True})
		# print usr
	elif (login_user_name!=usr):
		return render_to_response("index.html",{'anchor':True})

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
	try:
		if (user_password==user_repassword):
			cursor.execute('''INSERT INTO login(Username,Email,Password) values(?,?,?)''', (user_name,user_email,user_password))
			result = db.userdata.insert_one({"username":user_name,"stocks":[]})
			connection.commit()
			connection.close()
			return render_to_response("index.html",{'signup':True})
	except Exception as exp:
		return render_to_response("index.html",{'userexists':True})
	else:
		return render_to_response("index.html",{'signupfalse':True})


def forgot(request):
	return render_to_response("forgot.html",{'anchor':True})

