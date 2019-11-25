#!/usr/bin/env python3

import argparse
import pathlib
import csv
import typing as T
import difflib
from datetime import datetime,timedelta,date
import statistics

stock_codes = []
min_date = None
max_date = None
stock_data = {}
stock_dates = []
stock_prices = []
stock_diff = []
start_date = None
end_date = None

def resetStockData():
  global min_date,max_date,stock_data,stock_dates,stock_prices,stock_diff,start_date,end_date
  
  min_date = None
  max_date = None
  stock_data = {}
  stock_dates = []
  stock_prices = []
  stock_diff = []
  start_date = None
  end_date = None


def initStockPicker(filepath):
  global stock_codes
  with open(filepath, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
      stock_codes.append(row["StockName"])

def validateStockCode(stock_code):
  if(not stock_code in  stock_codes):
    closest_code = difflib.get_close_matches(stock_code, stock_codes, n=1)
    if(len(closest_code)==0):
      new_stock_code = input("[x] Stock Not Found!\n=> Re-Enter Stock Code : ")
      return False,new_stock_code
    answer = input(f"[!] Did you mean {closest_code[0]} ? (yes|no) : ").lower()
    if(answer=="yes"):
      return True,closest_code[0]
    else:
      new_stock_code = input("=> Re-Enter Stock Code : ")
      return False,new_stock_code
  return True,stock_code

def getStockCode(filepath):
  global stock_data,min_date,max_date
  with open(filepath, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    stock_code = input("=> Enter Stock Code : ")
    code_valid = False
    while(not code_valid):
      code_valid,stock_code = validateStockCode(stock_code.upper())
    for row in csv_reader:
      if(row["StockName"]==stock_code):
        stock_data[row["StockDate"]] = float(row["StockPrice"])
        date = datetime.strptime(row["StockDate"],'%d-%b-%Y').date()
        if(min_date is None and max_date is None):
          min_date = max_date = date
        if(date<min_date):
          min_date = date
        if(date>max_date):
          max_date = date


def validateDate(date,dtype):
  for fmt in ('%d-%b-%Y','%d-%m-%Y','%d/%b/%Y','%d/%m/%Y','%Y-%b-%d','%Y-%m-%d','%Y/%b/%d','%Y/%m/%b'):
    try:
      date = datetime.strptime(date,fmt).date()
      if(dtype=="End" and date <= start_date):
        print("[x] End Date should be greater that Start date! ")
        new_date = input("=> Re-Enter End Date : ")
        return False, new_date
      elif(date<min_date or date>max_date):
        if(dtype=="Start"):
          answer = input(f"[x] Date out of range! Do you want to set (Start date) to {min_date.strftime(fmt)} ? (yes|no) : ").lower()
          if(answer=="yes"):
            return True, min_date
          else:
            break
        elif(dtype=="End"):
          answer = input(f"[x] Date out of range! Do you want to set (End date) to {max_date.strftime(fmt)} ? (yes|no) : ").lower()
          if(answer=="yes"):
            return True, max_date
          else:
            break
      else:
        return True, date
    except ValueError:
      pass
  new_date = input(f"[x] Date not Valid!\n=> Re-Enter {dtype} Date : ")
  return False, new_date

def getStockDates():
  global start_date,end_date
  date_valid = False
  start_date = input("=> Enter Start Date : ").upper()
  while(not date_valid):
    date_valid, start_date = validateDate(start_date,'Start')

  date_valid = False
  end_date = input("=> Enter End Date : ").upper()
  while(not date_valid):
    date_valid, end_date = validateDate(end_date,'End')

def parseStockData():
  delta = end_date - start_date
  for i in range(delta.days+1):
    date = (start_date + timedelta(days=i)).strftime('%d-%b-%Y')
    if(date in stock_data):
      if(len(stock_dates)==0):
        stock_diff.append(0.0)
      else:
        stock_diff.append(stock_data[date] - stock_prices[-1])
      stock_prices.append(stock_data[date])
      stock_dates.append(date)
    else:
      if(len(stock_dates)>0):
        stock_diff.append(0.0)
        stock_prices.append(stock_prices[-1])
        stock_dates.append(date)


def maxProfit(array):
	max_so_far = 0
	max_ending_here = 0
	start = 0
	end = 0
	s = 0
	for i in range(0,len(array)): 
		max_ending_here += array[i] 
		if max_so_far < max_ending_here: 
			max_so_far = max_ending_here 
			start = s 
			end = i 
		if max_ending_here < 0: 
			max_ending_here = 0
			s = i+1
	return start,end,max_so_far
      
 
def getOutput():
  if(len(stock_prices)>2):
    print("\n******* Output *******\n")
    print(f"Median : {statistics.mean(stock_prices):.2f}")
    print(f"Std : {statistics.stdev(stock_prices):.2f}")
    i,j,profit = maxProfit(stock_diff)
    if(i!=j or profit!=0):
      print(f"Buy Date : {stock_dates[i]}")
      print(f"Sell Date : {stock_dates[j]}")
      print(f"Profit : Rs. {(profit*100):.2f} (For 100 shares)")
    else:
      print("[!] No Profitable purchases can be made!")
    print("\n******* xxxxxx *******\n")
  else:
    print("[x] Insufficient Data Points, Try Different Dates or Stocks!")

def stockPicker(filepath):
  initStockPicker(filepath)
  getStockCode(filepath)
  getStockDates()
  parseStockData()
  getOutput()

class StockDataSchema(T.NamedTuple):
    StockName: str
    StockDate: str
    StockPrice: float

    @classmethod
    def from_row(cls, row: dict):
        return cls(**{
            key: type_(row[key]) for key, type_ in cls._field_types.items()
        })

def validateCSV(filepath):
  with open(filepath, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
      try:
          StockDataSchema.from_row(row)
      except:
          return False
    return True


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Stock Picker v1 @author=Surya T")
  parser.add_argument("filepath",type=str,help="Path to CSV file")
  args = parser.parse_args()
  filepath = args.filepath
  if(filepath==None):
    parser.error("Specify path to CSV file")
  elif(not pathlib.Path(filepath).exists()):
    print("[x] File Does Not Exist!")
  elif(not validateCSV(filepath)):
    print("[x] Not Valid CSV File or Corrupted Data!")
  else:
    do_exit = False
    while(not do_exit):
      stockPicker(filepath)
      answer = input("Do you wish to continue ? (yes|no) : ").lower()
      if(answer=="yes"):
        print("\n")
        resetStockData()
      else:
        do_exit = True
 
