# -*- coding: utf-8 -*-
"""
Created on Fri May  1 10:11:52 2020

@author: jmyou
"""



#custom packages
import sec_database_functions as secdf

#where you want your files to go
directory = 'E:/PythonProjects/SEC_DataBase/data'

#where files are normally downloaded on your computer
download_dir = 'C:/Users/jmyou/Downloads'


#webdriver instance and options
driver = secdf.Chrome_Drive()

#generates tickers of all NASDAQ companies
tickers = secdf.open_list('companylist')

#downloads documents6
secdf.super_miner(driver, tickers,directory,download_dir)

