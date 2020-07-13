# -*- coding: utf-8 -*-
"""
Created on Sun May  3 15:50:53 2020

@author: jmyou
"""


import csv
import os
import pandas as pd
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
import shutil
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def Chrome_Drive():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    driver = webdriver.Chrome("C:/Users/jmyou/Downloads/chromedriver_win32/chromedriver.exe")
    
    return driver

def Fox_Drive():
    options = Options()
    options.binary_location = "C:/Users/jmyou/Desktop/geckodriver-v0.26.0-win32/geckodriver.exe"
    ex_path = "C:/Users/jmyou/Desktop/geckodriver-v0.26.0-win32/geckodriver.exe"
    driver = webdriver.Firefox(executable_path=ex_path)
    
    return driver


def open_list(file):
    """opens and formats downloaded stock data from nasdaq.com"""
    #makes sure the input filename has '.csv' extension
    if '.csv' in file:
        filename = file
    else:
        filename = file + '.csv'
    
    #lists for database information    
    tickers = []
    
    #opens file
    with open(filename,'r') as csvfile:
        securities = csv.reader(csvfile, delimiter=',', quotechar='|')
        
        #populates the various data lists with proper entries
        for row in securities:
           tickers.append(row[0])
           
    #assign headers to headers list
    headers = [tickers[0]]    
    
    #remove headers from other lists
    tickers.remove(tickers[0])
    
    
    #remove quotation marks from strings
    for i in range(len(tickers)):
        tickers[i] = tickers[i].replace('"',"")
        
    return tickers

"""generates a folder for a company and moves all downloaded files into that 
directory"""
def generate_ticker_directory(ticker,old_path,new_path):
    all_files = os.listdir(old_path)
    if os.path.isdir(new_path):
        for file in all_files:
            if ticker in file:
                shutil.move(old_path + '/' + file,new_path + '/' + file)
    else:
        os.mkdir(new_path)
        for file in all_files:
            if ticker in file:
                shutil.move(old_path + '/' + file,new_path + '/' + file)    

    
"""updates the url table which will be saved as a csv file"""    
def update_table(dic,url_table,path):
    for key, value in dic.items():
         for key2, value2 in value.items():
            item = []
            doc_name = key + '_' + key2
            item.append(doc_name)
            item.append(value2)
            url_table.append(item)
            
        
    if url_table[0][0] == 'Document':
        del(url_table[0])
    
    column_names = ['Document','Url']
    url_table = pd.DataFrame(url_table,columns=column_names)
    url_table.to_csv(path)


"""updates document url database"""
def update_urls(dic,path):
    
    url_table = []  
    try:
        with open(path, newline='') as csvfile:
                reader = csv.reader(csvfile,delimiter=',')
                for row in reader:
                    url_table.append(row[1:])
                    
                    
        update_table(dic, url_table,path)
    
    except FileNotFoundError:
        update_table(dic,url_table,path)
        

"""gets the date that the document was filed on"""
def get_date(driver,all_headers_path):
    
    #gets document filing date and type 
    all_headers = driver.find_elements_by_xpath(all_headers_path)
    if len(all_headers) == 7:
        date = all_headers[4].text
    elif len(all_headers) == 8:
        date = all_headers[2].text
    elif len(all_headers) == 9:
        date = all_headers[2].text
    elif len(all_headers) == 5:
        date = all_headers[2].text
    elif len(all_headers) == 4:
        date = all_headers[2].text
    elif len(all_headers) == 3:
        date = all_headers[1].text
    elif len(all_headers) == 14:
        date = all_headers[2].text
    else:
        date = 'DATE'
        print(len(all_headers))
        
    if '\n' in date:
        date = date.rsplit('\n')[0]
        
    date = date.replace(' ','').replace('.','_').replace(',','_')
    
    return date

"""returns the document type i.e. 10K,10KA,etc"""
def get_doc_type(driver,basic_info_path):
    #returns document type from page 
    
    info = driver.find_elements_by_xpath(basic_info_path)
    doc_type = 'DOC'
    for element in info:
        if element.text == '10-K':
            doc_type = '10_K'
            break
        elif element.text == '10-K/A':
            doc_type = '10_K_A'
            
            break
        else:
            doc_type = 'DOC'
            
    
    return doc_type

"""retrieves a list of documents available for download from the pages html code"""
def get_forms(driver,ticker):
    
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK=' + ticker + '&owner=exclude&action=getcompany'
    
    filing_search_field_path = '//input[@name="type"]'
    search_button_path = '//input[@type="submit"]'
    num_results = '//select[@name="count"]'
    results_100 = '//option[@value="100"]'
    row_path = '//a[@id="interactiveDataBtn"]'

    #data mining
    driver.get(url)
    
 
    search_bar = driver.find_element_by_xpath(filing_search_field_path)
    search_bar.click()
    search_bar.send_keys('10-K')
    entries_button = driver.find_element_by_xpath(num_results)
    entries_button.click()
    results = driver.find_element_by_xpath(results_100)
    results.click()
    search_button = driver.find_element_by_xpath(search_button_path)
    search_button.click()
    time.sleep(2)
    url_10k = driver.current_url
    driver.get(url_10k)
    forms = driver.find_elements_by_xpath(row_path)
    
    return forms

"""removes any files named 'Financial_Report from the database directory"""
def file_delete(i,ticker):
    
    path = 'C:/Users/jmyou/Downloads'

    files = ['Financial_Report.xlsx',
             'Financial_Report.xls',
             'Financial_Report (1).xlsx',
             'Financial_Report (1).xls',
             'Financial_Report (2).xlsx',
             'Financial_Report (2).xls',
             'Financial_Report (3).xlsx',
             'Financial_Report (3).xls',]
    
    
    
    for e in files:
        if os.path.isfile(path + '/' + e) == True:
            os.remove(path + '/' + e)
            
    

"""Renames and moves downloaded document files"""
def rename_and_move_file(ticker,date,doc_type,directory,download_dir):
    time.sleep(4)
    if date == '':
        date = 'DATE'
    
    
    
    
    tag = ticker + '_' + doc_type + '_' + date
  
    
    
    if os.path.isfile(download_dir + '/Financial_Report.xlsx'):
        old_name = download_dir + '/Financial_Report.xlsx'
        new_name = download_dir + '/' + tag + '.xlsx'
        new_path = directory + '/' + tag + '.xlsx'
        os.rename(old_name,new_name)
        shutil.move(new_name,new_path)
    elif os.path.isfile(download_dir + '/Financial_Report.xls'):
        old_name = download_dir + '/Financial_Report.xls'
        new_name = download_dir + '/' + tag + '.xls'
        new_path = directory + '/' + tag + '.xls'
        os.rename(old_name,new_name)
        shutil.move(new_name,new_path)
    else:
        print('this aint working')
                    

"""mines data by downloading documents from the SEC website"""
def stock_miner(driver,
                url,
                ticker,
                forms,url_10k,
                row_path,all_headers_path,
                basic_info_path,
                sub_document_path,
                commands_path,
                company_dic,
                directory,
                download_dir):
    
    
    complete = []
    incomplete = []
    #start of document loop
    for i in range(len(forms)):
        driver.get(url_10k)
        time.sleep(4)
        forms = driver.find_elements_by_xpath(row_path)
        
        try:
            forms[i].click()
        except ElementClickInterceptedException:
            print('error')
            time.sleep(5)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            forms[i].click()
    
            
        driver.get(driver.current_url)
        
        #gets document filing date  
        date = get_date(driver, all_headers_path)
        
        #gets document type
        doc_type = get_doc_type(driver, basic_info_path)
        
        
        # loads all subdocuments into document report    
        try:
            sub_docs = driver.find_elements_by_xpath(sub_document_path)
            sub_docs[len(sub_docs)-1].click()
            
            
            #downloads all subdocuments into one document report
            commands = driver.find_elements_by_xpath(commands_path)
            commands[1].click()
            
            #adds url to database
            url_code = doc_type + '_' + date
            company_dic[url_code] = driver.current_url
            
            #renames and moves downloaded spreadsheets
            try:
                rename_and_move_file(ticker, date, doc_type,directory,download_dir)
                complete.append(i)
                print(ticker + ' doc: ' + str(i) + ' completed')
            except FileNotFoundError:
                incomplete.append(i)
                
            
            #removes 'Financial Report.xlsx' from downloads so there is no issue the next
            #time the script is run
            
        except IndexError:
            try:
                driver.get(url)
                time.sleep(3)
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                sub_document_path = '//ul[@id="menu"]//a'
                sub_docs = driver.find_elements_by_xpath(sub_document_path)
                sub_docs[len(sub_docs)-1].click()
                        
                #downloads all subdocuments into one document report
                commands = driver.find_elements_by_xpath(commands_path)
                commands[1].click()
                
                #adds url to database
                url_code = doc_type + '_' + date
                company_dic[url_code] = driver.current_url
                time.wait(3)
                #renames and moves downloaded spreadsheets
                try:
                    rename_and_move_file(ticker, date, doc_type,directory,download_dir)
                    complete.append(i)
                    print(ticker + ' doc: ' + str(i) + ' completed')
                except FileNotFoundError:
                    incomplete.append(i)
                
                
                #removes 'Financial Report.xlsx' from downloads so there is no issue the next
                #time the script is run
                
                complete.append(i)
            except IndexError:
                file_delete(i,ticker)
                incomplete.append(i)
                continue

    return complete, incomplete


def second_pass_miner(driver,
                      ticker,
                      complete,
                      incomplete,
                      fail_dic,
                      url,
                      url_10k,
                      row_path,
                      all_headers_path,
                      basic_info_path,
                      sub_document_path,
                      commands_path,
                      company_dic,
                      directory,
                      download_dir):
    
    
    for element in incomplete:
        driver.get(url_10k)
        time.sleep(4)
        forms = driver.find_elements_by_xpath(row_path)
        
        try:
            forms[element].click()
        except ElementClickInterceptedException:
            print('error')
            time.sleep(5)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            forms[element].click()
    
            
        driver.get(driver.current_url)
        
        #gets document filing date  
        date = get_date(driver, all_headers_path)
        
        #gets document type
        
        doc_type = get_doc_type(driver, basic_info_path)
        
        # loads all subdocuments into document report    
        try:
            sub_docs = driver.find_elements_by_xpath(sub_document_path)
            sub_docs[len(sub_docs)-1].click()
            
            
            #downloads all subdocuments into one document report
            commands = driver.find_elements_by_xpath(commands_path)
            commands[1].click()
            
            #adds url to database
            url_code = doc_type + '_' + date
            company_dic[url_code] = driver.current_url
            
            #renames and moves downloaded spreadsheets
            rename_and_move_file(ticker, date, doc_type,directory,download_dir)
            
            
            #removes 'Financial Report.xlsx' from downloads so there is no issue the next
            #time the script is run
            complete.append(element)
            print(ticker + ' doc: ' + str(element) + ' completed')
            
        except IndexError:
            try:
                driver.get(url)
                time.sleep(3)
                driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                sub_document_path = '//ul[@id="menu"]//a'
                sub_docs = driver.find_elements_by_xpath(sub_document_path)
                sub_docs[len(sub_docs)-1].click()
                        
                #downloads all subdocuments into one document report
                commands = driver.find_elements_by_xpath(commands_path)
                commands[1].click()
                
                #adds url to database
                url_code = doc_type + '_' + date
                company_dic[url_code] = driver.current_url
                
                #renames and moves downloaded spreadsheets
                rename_and_move_file(ticker, date, doc_type,directory,download_dir)
                
                
                #removes 'Financial Report.xlsx' from downloads so there is no issue the next
                #time the script is run
                
                complete.append(element)
                print(ticker + ' doc: ' + str(element) + ' completed')
                
            except IndexError:
                print(str(element) + ' failed')
                
        return company_dic

def update_bad_tickers(fail,path):
    if os.path.exists(path):
        ticker_list = []
        with open(path, newline='') as csvfile:
                        reader = csv.reader(csvfile,delimiter=',')
                        for row in reader:
                            if row[1] == 'Tickers':
                                continue
                            else:
                                ticker_list.append(row[1])
                                
        ticker_list.append(fail)
        columns = ['Tickers']                
        ticks = pd.DataFrame(ticker_list,columns=columns)
        ticks.to_csv(path)
    else:
        ticker_list = []
        ticker_list.append(fail)
        columns = ['Tickers']               
        ticks = pd.DataFrame(ticker_list,columns=columns)
        ticks.to_csv(path)


def get_bad_tickers(path):
    if os.path.isdir(path):
        ticker_list = []
        with open(path, newline='') as csvfile:
                        reader = csv.reader(csvfile,delimiter=',')
                        for row in reader:
                            if row[1] == 'Tickers':
                                continue
                            else:
                                ticker_list.append(row[1])
    else:
        ticker_list = []
        
    return ticker_list



def super_miner(driver,tickers,directory,download_dir):
    main_dic = {}
    fail_dic = {}
    
    #relevant webpage elements
    filing_search_field_path = '//input[@name="type"]'
    search_button_path = '//input[@type="submit"]'
    num_results = '//select[@name="count"]'
    results_100 = '//option[@value="100"]'
    all_headers_path = '//table[@class="report"]/tbody/tr/th'
    sub_document_path = '//ul[@id="menu"]/li/a'
    commands_path = '//table/tbody/tr/td[@colspan="2"]/a'
    basic_info_path = '//div[@class="companyInfo"]/p[@class="identInfo"]/strong'
    row_path = '//a[@id="interactiveDataBtn"]'
    
    bad_tickers_file = 'E:/PythonProjects/SEC_DataBase/data/DNE_Tickers.csv'
    bad_tickers = get_bad_tickers(bad_tickers_file)
    
    #main loop: loops over each company represented in tickers
    
    for ticker in tickers:
        if ticker in bad_tickers:
            continue
        else:
            time.sleep(3)
            path = directory + '/' + ticker
            old_path = directory + '/'
            
            # if a complete folder exists for a company, then the script moves to the 
            #next company in the tickers list
            if os.path.isdir(path):
                continue
            else:
                company_dic = {}
                url = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK=' + ticker + '&owner=exclude&action=getcompany'
                
                #loads company page on EDGAR databse
                driver.get(url)
                
                
                try:
                    #loads page with all 10K files listed
                    search_bar = driver.find_element_by_xpath(filing_search_field_path)
                    search_bar.click()
                    search_bar.send_keys('10-K')
                    entries_button = driver.find_element_by_xpath(num_results)
                    entries_button.click()
                    results = driver.find_element_by_xpath(results_100)
                    results.click()
                    search_button = driver.find_element_by_xpath(search_button_path)
                    search_button.click()
                    time.sleep(2)
                    url_10k = driver.current_url
                    driver.get(url_10k)
                    
                    #gets list of document to be downloaded
                    forms = driver.find_elements_by_xpath(row_path)
            
                    #downloads documents and generates lists of which documents
                    #were succesfully downloaded (complete) and failed downloads (incomplete)
                    complete, incomplete = stock_miner(driver, 
                        url, 
                        ticker, 
                        forms, 
                        url_10k, 
                        row_path, 
                        all_headers_path, 
                        basic_info_path, 
                        sub_document_path, 
                        commands_path, 
                        company_dic,
                        directory,
                        download_dir)
                                            
                            
                    #retries downloading files in the incomplete list
                    second_pass_miner(driver, 
                                            ticker, 
                                            complete, 
                                            incomplete, 
                                            fail_dic, 
                                            url, 
                                            url_10k, 
                                            row_path, 
                                            all_headers_path, 
                                            basic_info_path, 
                                            sub_document_path, 
                                            commands_path, 
                                            company_dic,
                                            directory,
                                            download_dir)
                                
                    #adds all company entries to the main dictionary
                    main_dic[ticker] = company_dic
                 
                except NoSuchElementException:
                    update_bad_tickers(ticker, bad_tickers_file)
                    continue
                
                #if all files are downloaded succesfully, the files are placed into
                # a sub-directory based on the filing company
                if len(forms) > 0:
                    if len(complete) == len(forms):
                        generate_ticker_directory(ticker, old_path, path)
                    else:
                        continue
                else:
                    continue
        
                #updates the Url Database
                # secdf.update_urls(main_dic, 'C:/Users/jmyou/Desktop/SEC_DATABASE/Url_Table.csv')
                
                # #updates the failed Url Database
                # secdf.update_urls(fail_dic, 'C:/Users/jmyou/Desktop/SEC_DATABASE/Failed_Url_Table.csv')