from selenium import webdriver
import time
import pandas as pd
import os
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def scrape(temp):
    temp = temp.split(' ')
    ur = ""
    for i in range(0,len(temp)):
        if i==len(temp)-1:
            ur+=temp[i]
        else:
            ur+=temp[i]+"%20"

    url1 = str('https://www.linkedin.com/jobs/search/?currentJobId=3364877951&geoId=106187582&keywords=' + ur + '&location=Delhi%2C%20India&refresh=true')

    driver = webdriver.Chrome(executable_path=r'C:\Users\Aravo\OneDrive\Desktop\website\website\chromedriver.exe')
    driver.implicitly_wait(10)
    driver.get(url1)

    j = 2
    while j <= int((100+200)/25)+1: 
        driver.execute_script("window.scrollTo(0, 10000);")
        j = j + 1
        
        try:
            send=driver.find_element(By.XPATH, "//button[@aria-label='Load more results']")
            driver.execute_script("arguments[0].click();", send)   
            time.sleep(3)
        except:
            pass
            time.sleep(5)

    companyname= []
    titlename= []

    try:
        for i in range(j):
            company=driver.find_elements(By.CLASS_NAME, "base-search-card__subtitle")[i].text
            companyname.append(company)
    except IndexError:
        print("no")

    try:
        for i in range(j):
            title=driver.find_elements(By.CLASS_NAME, "base-search-card__title")[i].text
            titlename.append(title)
    except IndexError:
        print("no")

    companyfinal=pd.DataFrame(companyname,columns=["company"])
    titlefinal=pd.DataFrame(titlename,columns=["title"])

    x=companyfinal.join(titlefinal)

    x.to_csv(r'C:\Users\Aravo\OneDrive\Desktop\website\website\Jobs.csv')
            
    jobList = driver.find_elements(By.CLASS_NAME, "base-card__full-link")
    hrefList = []
    for e in jobList:
        hrefList.append(e.get_attribute('href'))

    linklist=pd.DataFrame(hrefList,columns=["joblinks"])
    linklist.to_csv(r"C:\Users\Aravo\OneDrive\Desktop\website\website\Links.csv")

    driver.close()
    
        
    
    