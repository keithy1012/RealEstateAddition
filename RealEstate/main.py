#Importing Stuff
import csv
from random import random, randint
from time import sleep
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from selenium import webdriver
from selenium.common import exceptions
from msedge.selenium_tools import Edge, EdgeOptions
from sklearn import *
from sklearn import preprocessing, svm, ensemble
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
#------------------------------------------------------------
#Creating Web Driver to Scrape Zillow
def CreateWebDriver():
    driver  = webdriver.Chrome(executable_path='chromedriver.exe')
    return driver

#Creating a .csv file using the zipcode that user puts in (Ex. 08820.csv)
def generate_filename(Zip_Code):
    stem = path = '_'.join(Zip_Code.split(' '))
    global filename
    filename = stem + '.csv'
    return filename

#Creating the URL that is used to scrape the website
def generate_url(Zip_Code):
    Zip_Code = Zip_Code.replace(' ', '+')
    url_template = 'https://www.zillow.com/homes/for_sale/{ZipCode}_rb/'.format(ZipCode=Zip_Code)
    return url_template

#Sleeping allows for all the data on a website to load before moving on 
def sleep_for_random_interval():
    time_in_seconds = random() * 2
    sleep(time_in_seconds)

#Writing data into the csv file we created
def save_data_to_csv(record, filename, new_file=False):
    header = ['address', 'sqft', 'price', 'Bedroom_Count', 'Bath_Count', 'Duration']
    if new_file:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    else:
        with open(filename, 'a+', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(record)

#Collecting all records on the page
def collect_product_cards_from_page(driver):
    cards = driver.find_elements_by_xpath('//article[@role="presentation"]')
    return cards

#Run the webscraper
def run(search_term):
    filename = generate_filename(search_term) #generate new file
    save_data_to_csv(None, filename, new_file=True)  # initialize a new file
    driver = CreateWebDriver() #initialize the web driver 
    num_records_scraped = 0 #keeps track of number of records
    search_url = generate_url(Zip_Code) #search_url variable is the generated URL link
    print(search_url) #printing url to make sure it is correct
    driver.get(search_url) #start running the webdriver 
    time.sleep(15) #sleeping to ensure all data is loaded before continuing
    cards = collect_product_cards_from_page(driver) #getting info for all elements on page
    for card in cards:
            record = GetInfo(card)
            if record:
                save_data_to_csv(record, filename)
                num_records_scraped += 1
    sleep_for_random_interval() 
    driver.quit() #closing the driver
 
#This function looks in every record and identifies every important element
def GetInfo(card):
    global address
    global price
    global otherInfo
    global sqft
    global bedcount
    global bathcount
    try: #finds address
        address = card.find_element_by_class_name('list-card-addr').text.strip()
    except exceptions.NoSuchElementException:
        address='None For Address'
 
    try: #finds price
        price = card.find_element_by_class_name('list-card-price').text.strip()
    except exceptions.NoSuchElementException:
        price = 'None For Price'
    
    try: #entire string that includes sqft, bedroom, and bathroom
        otherInfo = card.find_element_by_class_name("list-card-details").text.strip()
    except exceptions.NoSuchElementException:
        price = 'None For Details'
    index = otherInfo.find("sqft")
    sqft = otherInfo[index-6:index-1]
    index = otherInfo.find("bds")
    bedcount = otherInfo[index-2:index-1]
    index = otherInfo.find("ba")
    bathcount = otherInfo[index-2: index-1]

    #Still trying to get heating/cooling, duration on Zillow, year built, neighborhood score
    return address, sqft, price, bedcount, bathcount
 
#reading in csv and generating fake dataframes as practice
'''originally 40 real elements, so I created 2 more dataframes and used random numbers to generate fake, but reasonable data
'''
def getCSV(filename):
    global data
    dataset1 = pd.read_csv(filename)
    DataCleanUp(dataset1)
    print("Old Data Describe: ", dataset1.describe())
    dataset2 = dataset1
    dataset2.price = dataset2.price+randint(1000, 10000) #First fake dataset generates new price and new bedroom count
    dataset2.Bedroom_Count = dataset2.Bedroom_Count+randint(0,2)
    dataset3=dataset1
    dataset3.price = dataset3.price + randint(-1000, 10000) #Second fake dataset generates new price and new bathroom count
    dataset3.Bath_Count = dataset3.Bath_Count + randint(0,2)
    data = dataset1.append(dataset2)
    data = data.append(dataset3)
    print("Data Describe: \n" , data.describe())
    print("Whole Data: \n" , data)
    save_data_to_csv(data, filename)
 
    
def DataCleanUp(data):
    for ind in data.index:
        data['price'][ind] =data['price'][ind].replace(',','')
        data['price'][ind] =data['price'][ind].replace('$','')
        if data['price'][ind].isnumeric() == False:
            data['price'][ind] = data['price'][ind].replace(data['price'][ind],str(randint(50000, 100000)))  



        if (len(str(data['sqft'][ind]))==0):
            data['sqft'][ind] = data['sqft'][ind].replace(data['sqft'][ind],str(randint(500, 5000)).replace(',',''))  


        if type(data['sqft'][ind])==str: 
            data['sqft'][ind] = data['sqft'][ind].replace(',','')
            if data['sqft'][ind].isnumeric() == False:
                data['sqft'][ind] = data['sqft'][ind].replace(data['sqft'][ind],str(randint(500, 5000)).replace(',',''))
        if type(data['Bedroom_Count'][ind])==str and data['Bedroom_Count'][ind].isnumeric() == False:
            data['Bedroom_Count'][ind] = data['Bedroom_Count'][ind].replace(data['Bedroom_Count'][ind],str(randint(1, 3)))   
        if type(data['Bath_Count'][ind])==str and data['Bath_Count'][ind].isnumeric() == False:
            data['Bath_Count'][ind] = data['Bath_Count'][ind].replace(data['Bath_Count'][ind],str(randint(1, 3))) 
    save_data_to_csv(data, filename)  
    data[['price', 'sqft', 'Bedroom_Count', 'Bath_Count']] = data[['price', 'sqft', 'Bedroom_Count', 'Bath_Count']].apply(pd.to_numeric)
 
#plots the points using matplotlib
def PlotPoints(data):
    #_______ Price vs Sqft __________ #
    plt.title('Price vs. Sqft')
    plt.scatter(data['sqft'],data.price)
    plt.ylabel('Price (in millions)')
    plt.xlabel('Square Feet')
    #machine learning for price vs sqft
    X = np.array(data['sqft']).reshape(-1, 1)
    y = np.array(data['price']).reshape(-1, 1)
    X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.15, random_state=0)
    regr = LinearRegression()
    global line
    line = regr.fit(X_train, y_train)
    print("Intercept: ", line.intercept_[0])
    print("Slope: ", line.coef_[0])
    print("Formula: Sqft = " , line.coef_[0] , '* Price + ' , line.intercept_[0])
    x = float(input("Sqft?"))
    print(PredictPriceWithSqft(x, line.intercept_[0], line.coef_[0].astype(float)))
    print("Score: ", "{:.4f}".format(regr.score(X_test, y_test)))
    y_pred = regr.predict(X_test)
    plt.scatter(X_test, y_test, color ='b')
    plt.plot(X_test, y_pred, color ='k')
    clf = ensemble.GradientBoostingRegressor(n_estimators=400, max_depth=5, min_samples_split=2, learning_rate=0.1, loss='ls')
    clf.fit(X_train, y_train)
    print('After Gradient Boosting Accuracy Score:', "{:.4f}".format(clf.score(X_test, y_test)))
    y_pred = regr.predict(X_test)
    #_______ Bds vs. Price __________ #
    plt.figure(2)
    plt.title('Bedroom vs. Price')
    data['Bedroom_Count'] = data['Bedroom_Count'].astype(float)
    plt.scatter(data.Bedroom_Count, data.price)
    plt.ylabel('Price (in millions)')
    plt.xlabel('Bedroom Count')
    #_______ Bath vs. Price __________ #
    plt.figure(3)
    plt.title('Bathroom vs. Price')
    data['Bath_Count'] = data['Bath_Count'].astype(float)
    plt.scatter(data.Bath_Count, data.price)
    plt.ylabel('Price (in millions)')
    plt.xlabel('Bathroom Count')
    plt.show()
 
#----------------------------------------------------
def PredictPriceWithSqft(SqftValue, Yint, slope):
    global PredictedPriceWithSqft
    PredictedPriceWithSqft = slope * SqftValue + Yint
    PredictedPriceWithSqft = PredictedPriceWithSqft[0].astype(float)
    PredictPrice = "{:.2f}".format(PredictedPriceWithSqft)
    result =  "Your predicted price is: "+ PredictPrice
    return result
    
#----------------------------------------------------
#running through the main method
if __name__ == '__main__':
    global Zip_Code
    Zip_Code = input("What Zip Code?")
    run(Zip_Code)
    getCSV(filename)
    PlotPoints(data)
