import calendar
from datetime import date
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from selenium import webdriver
import pickle
from PIL import Image
from io import BytesIO
import os


#
# driver = webdriver.Chrome(executable_path="chromedriver.exe")
# # driver = webdriver.Chrome(executable_path="chromedriver.exe")
# url = "https://login.yahoo.com/config/login?"
# site = driver.get(url)


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
    driver = webdriver.Firefox(executable_path="geckodriver.exe")
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
    # driver = webdriver.Firefox()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    driver.get('https://www.yahoo.com/')
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)

    print("Starts here")
    print(driver.page_source)
    print("Ends here")

    #     url = "https://login.yahoo.com/config/login?"
    summary_base_url = "https://finance.yahoo.com/quote/{:s}/company360?p={:s}"
    base_marketable_url = "https://finance.yahoo.com/quote/{}"

    #     driver = webdriver.Chrome()
    #     site = driver.get(url)

    company_descriptions = []

    print(company_list)
    for i in company_list:
        url_summary = summary_base_url.format(i, i)
        url = base_marketable_url.format(i)

        driver.get(url_summary)
        html_source = driver.page_source
        source = BeautifulSoup(html_source)
        print(source)

        response = requests.get(url)
        data = response.text

        soup = BeautifulSoup(data, features="html.parser")

        soup.find_all('span', {'data-reactid': '14'})
        company_detail = soup.find_all('div', {
            'class': "D(ib) Mt(-5px) Mend(20px) Maw(56%)--tab768 Maw(52%) Ov(h) smartphone_Maw(85%) smartphone_Mend(0px)"})[
            0].text
        try:
            value = soup.find_all('span', {'class': 'Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)'})[0].text
        except:
            value = soup.find_all('span', {'class': 'Trsdu(0.3s) Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(b)'}) + " ADDED"
        percentage = soup.find_all('span', {'data-reactid': '16'})[0].text
        description = soup.find_all('span', {'data-reactid': '18'})[0].text
        try:
            previous_close = soup.find_all('span', {'data-reactid': '16'})[1].text
        except:
            previous_close = "234"

        company_abr = company_detail.split("-")[0]
        company_name = company_detail.split("-")[1]
        company_currency = company_detail.split("-")[2]
        company_title = "{:s}, Inc.({:s})".format(company_name, company_abr)

        try:
            summary = source.find_all("header", {"data-test": "comp360-summary"})[0].text
        except:
            summary = "Data is not made public by this company"
        try:
            image = driver.find_element_by_class_name('_29rOq').screenshot_as_png
            image = Image.open(BytesIO(image))  # uses PIL library to open image in memory
            img_url = 'static/img/graph/' + i + "_graph.png"
            image.save(img_url)
        except:
            img_url = "static/img/nodata.png"

        company_descriptions.append(
            (company_title,
             description,
             company_currency,
             previous_close,
             percentage,
             value,
             summary,
             img_url,
             url)
        )

    driver.close()
    # company_descriptions = [(' 1st Source CorporationNasdaqGS , Inc.(SRCE )',
    #                          'As of  1:51PM EDT. Market open.',
    #                          ' NasdaqGS Real Time Price. Currency in USD',
    #                          '31.85',
    #                          '+1.89 (+5.93%)',
    #                          '33.74',
    #                          "SRCE’s innovation outlook is neutral based on a current score of 27 out of 99, underperforming sector average. Jobs growth over the past year has increased and insiders sentiment is neutral. Over the past 4 quarters SRCE beat earnings estimates 2 times and it pays dividend lower than its peers",
    #                          'static/img/graph/SRCE_graph.png',
    #                          'https:/finance.yahoo.com/quote//SRCE'),
    #                         ("(Altigen Communications, Inc.Other OTC , Inc.(ATGN )",
    #                         'As of  1:03PM EDT. Market open.',
    #                         ' Other OTC Delayed Price. Currency in USD',
    #                         '1.4900',
    #                         '+0.0100 (+0.67%)',
    #                         '1.5000',
    #                         ' ',
    #                         'static/img/nodata.png',
    #                         'https:/finance.yahoo.com/quote/ATGN'),
    #                         ("(Altigen Communications, Inc.Other OTC , Inc.(ATGN )",
    #                          'As of  1:03PM EDT. Market open.',
    #                          ' Other OTC Delayed Price. Currency in USD',
    #                          '1.4900',
    #                          '+0.0100 (+0.67%)',
    #                          '1.5000',
    #                          ' ',
    #                          'static/img/nodata.png',
    #                          'https:/finance.yahoo.com/quote/ATGN')
    #                         ]
    #
    # print(company_descriptions)
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
    company_descriptions = get_company_details(company_list[:5])

    print(company_list)
    stuff_for_frontend = {
        'company_list': company_list,
        'company_descriptions': company_descriptions,

    }
    return render(request, 'stock/index.html', stuff_for_frontend)
