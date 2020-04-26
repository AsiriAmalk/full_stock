import calendar
from datetime import date
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from selenium import webdriver
import time
import os

# GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
# CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
# driver = webdriver.Chrome(executable_path="chromedriver.exe")
# # driver = webdriver.Chrome(executable_path="chromedriver.exe")
# url = "https://login.yahoo.com/config/login?"
# site = driver.get(url)

CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"


# def get_summary(company_abr, driver=driver):
#     summary_base_url = "https://finance.yahoo.com/quote/{:s}/company360?p={:s}"
#     url = summary_base_url.format(company_abr, company_abr)
#     print(url)
#     driver.get(url)
#     html_source = driver.page_source
#     source = BeautifulSoup(html_source)
#     #     print(url)
#     #     print(company_abr)
#     #     print(source)
#     return source.find_all("header", {"data-test": "comp360-summary"})[0].text


def open_browser(request):
    driver = webdriver.Chrome(executable_path="chromedriver.exe")
    url = "https://finance.yahoo.com/"
    site = driver.get(url)
    return render(request, "base.html")


def get_company_list(date_):
    base_company_url = "https://finance.yahoo.com/calendar/earnings?day={}"

    company_list_url = base_company_url.format(date_)

    try:
        response = requests.get(company_list_url)
        data = response.text

        soup = BeautifulSoup(data, features="html.parser")
        company_list = [i.text for i in soup.find_all('a', {'class': 'Fw(600)'})]
    except:
        company_list = ["Connection Error"]
    return company_list


def get_company_details(company_list):
    # chrome_options = webdriver.ChromeOptions()
    #
    # chrome_options.binary_location = '.apt/usr/bin/google-chrome-stable'
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('headless')
    #
    # driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
    # # driver = webdriver.Chrome(executable_path="chromedriver.exe")
    # url = "https://login.yahoo.com/config/login?"
    # site = driver.get(url)
    # driver.implicitly_wait(50)
    # time.sleep(50)
    # print("chrome_connected")

    # signin_button = driver.find_element_by_xpath("//*[@id=\"header-signin-link\"]")
    # signin_button.click()
    # driver.implicitly_wait(300)
    #
    # email_box = driver.find_element_by_xpath("//*[@id=\"login-username\"]")
    # email_box.send_keys("markeresearch@yahoo.com")
    # driver.implicitly_wait(300)
    # driver.find_element_by_xpath("//*[@id=\"login-signin\"]").click()
    # # sign_button.click()
    # driver.implicitly_wait(30)
    #
    # password_box = driver.find_element_by_xpath("//*[@id=\"login-passwd\"]")
    # password_box.send_keys("young123.")
    # password_button = driver.find_element_by_xpath("//*[@id=\"login-signin\"]")
    # password_button.click()

    #     url = "https://login.yahoo.com/config/login?"
    # summary_base_url = "https://finance.yahoo.com/quote/{:s}/company360?p={:s}"
    base_marketable_url = "https://finance.yahoo.com/quote/{}"

    #     driver = webdriver.Chrome()
    #     site = driver.get(url)

    company_descriptions = []

    print(company_list)
    for i in company_list:
        # url_summary = summary_base_url.format(i, i)
        url = base_marketable_url.format(i)

        # driver.get(url_summary)
        # html_source = driver.page_source
        # source = BeautifulSoup(html_source)

        response = requests.get(url)
        data = response.text

        soup = BeautifulSoup(data, features="html.parser")

        soup.find_all('span', {'data-reactid': '14'})
        company_detail = soup.find_all('div', {
            'class': "D(ib) Mt(-5px) Mend(20px) Maw(56%)--tab768 Maw(52%) Ov(h) smartphone_Maw(85%) smartphone_Mend(0px)"})[
            0].text
        value = soup.find_all('span', {'class': 'Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)'})[0].text
        percentage = soup.find_all('span', {'data-reactid': '16'})[0].text
        description = soup.find_all('span', {'data-reactid': '18'})[0].text
        previous_close = soup.find_all('span', {'data-reactid': '16'})[1].text

        company_abr = company_detail.split("-")[0]
        company_name = company_detail.split("-")[1]
        company_currency = company_detail.split("-")[2]
        company_title = "{:s}, Inc.({:s})".format(company_name, company_abr)
        summary = "Ok"
        # try:
        #     summary = source.find_all("header", {"data-test": "comp360-summary"})[0].text
        # except:
        #     summary = company_detail

        company_descriptions.append(
            (company_title,
             description,
             company_currency,
             previous_close,
             percentage,
             value,
             summary)
        )

    return company_descriptions


def home(request):
    return render(request, "base.html")


def all_stock(request):
    abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
    try:
        search_date = request.POST.get('search_date')
    except:
        search_date = str(date.today())

    month = abbr_to_num[search_date.split(" ")[0]]
    if len(str(month)) == 1:
        month = "0" + str(month)
    "2020-04-17"
    selected_date = "{:s}-{:s}-{:s}".format(search_date.split(" ")[2], month, search_date.split(" ")[1].split(",")[0])

    company_list = get_company_list(selected_date)
    company_descriptions = get_company_details(company_list)

    print(company_list)
    stuff_for_frontend = {
        'company_list': company_list,
        'company_descriptions': company_descriptions,

    }
    return render(request, 'stock/index.html', stuff_for_frontend)
