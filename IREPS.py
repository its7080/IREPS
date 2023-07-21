# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 18:45:47 2018
Python script to get the details from the tenders of Railway zones
@author: BanuPrakash
last update on June 1 2023 by Anupam Manna
"""

import os
import time

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
from datetime import datetime
import argparse
import sys
# import numpy as np
import pdfplumber
from requests.exceptions import ConnectTimeout


def get_main_page_data(URL):
    try:
        response = requests.get(URL)
        soup = BeautifulSoup(response.content, "lxml")
        table = soup.find('table', {'id': 'mytable'})
        rows = table.find_all('tr')[2:]
        region_tenders_link = [[row.find_all('td')[1].get_text(),
                                row.find_all('td')[2].get_text(),
                                row.find_all('td')[3].find('a')['href']] for row in rows]
        return region_tenders_link
    except Exception as e:
        print(e)
        print("COULDN'T CONNECT TO INTERNET")
        logging.debug(e)
        logging.info("COULDN'T CONNECT TO INTERNET")
        sys.exit()

def get_number_of_pages(URL):
    page_soup = BeautifulSoup(requests.get(URL).content, "lxml")
    number_of_pages = len(page_soup.find_all('a', {'style': 'text-decoration:underline; color:#0033FF;'})) + 1
    return number_of_pages


def get_title_advertised_value(URL):
    max_retries = 5
    retries = 0
    
    while retries < max_retries:
        try:
            response = requests.get(URL, timeout=5)  # Add a timeout to the request
            response.raise_for_status()  # Raise an exception if the request was unsuccessful
            response = requests.get(URL)
            with open("example.pdf", "wb") as f:
                f.write(response.content)

            with pdfplumber.open("example.pdf") as pdf:
                table = pdf.pages[0].extract_tables()[0]

            table = [[value for value in sublist if value is not None] for sublist in table]

            new_table = [row[i*2:i*2+2] for row in table for i in range(len(row) // 2)] + [row for row in table if len(row) <= 2]

            extracted_info = {}
            keys_to_extract = ['Name of Work', 'Bidding type', 'Bidding System', 'Date Time Of Uploading Tender', 'Pre-Bid Conference Date Time', 'Advertised Value', 'Earnest Money (Rs.)', 'Contract Type']

            for item in new_table:
                if item[0] in keys_to_extract and len(item) > 1:
                    extracted_info[item[0]] = item[1]

            name_of_work = extracted_info.get('Name of Work', '')
            bidding_type = extracted_info.get('Bidding type', '')
            bidding_system = extracted_info.get('Bidding System', '')
            date_time_of_uploading_tender = extracted_info.get('Date Time Of Uploading Tender', '')
            pre_bid_conference_date_time = extracted_info.get('Pre-Bid Conference Date Time', '')
            advertised_value = extracted_info.get('Advertised Value', '')
            earnest_money = extracted_info.get('Earnest Money (Rs.)', '')
            contract_type = extracted_info.get('Contract Type', '')

            tender_title = name_of_work
            return tender_title, advertised_value, bidding_type, bidding_system, date_time_of_uploading_tender, pre_bid_conference_date_time, earnest_money, contract_type
        except (ConnectTimeout, requests.exceptions.RequestException) as e:
            print(f"Connection error: {e}")
            print("Retrying...")
            retries += 1
            time.sleep(2)  # Add a delay before retrying the request
        
    print("Max retries exceeded. Skipping the request.")
    return None  # Return None or handle the failure case accordingly

def get_page_data(URL, zone, appending_list):
    page_soup = BeautifulSoup(requests.get(URL).content, "lxml")
    table = page_soup.find('table', {'id': 'mytable'})
    rows = table.find_all('tr')[1:]

    for count, row in enumerate(rows, start=1):
        logging.info(f"\t\tGetting from row {count} out of {len(rows)}")
        pdf_url = "https://www.ireps.gov.in" + row.find_all('td')[2].find('a')['href']
        time.sleep(1)
        tender_title, advertised_value, bidding_type, bidding_system, date_time_of_uploading_tender, pre_bid_conference_date_time, earnest_money, contract_type = get_title_advertised_value(pdf_url)
        if not tender_title:
            tender_title = row.find_all('td')[3].get_text()

        appending_list.append([
            zone,
            row.find_all('td')[1].get_text(),
            row.find_all('td')[2].get_text(),
            tender_title,
            re.sub('\s+', '', row.find_all('td')[4].get_text()),
            row.find_all('td')[5].get_text(),
            re.sub('\s+', '', row.find_all('td')[6].get_text()),
            advertised_value,
            pdf_url,
            bidding_type,
            bidding_system,
            date_time_of_uploading_tender,
            pre_bid_conference_date_time,
            earnest_money,
            contract_type
        ])
        time.sleep(1)

    return appending_list

if __name__ == '__main__':
    print("Dasd")
    if not os.path.exists('Logs'):
        os.makedirs('Logs')

    now = datetime.now()
    log_file = os.path.join('Logs', f'logs_{now.year}_{now.month}_{now.day}.log')
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        filename=log_file, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser(description='Script to Get tender details')
    parser.add_argument("-z", '--zone', dest='zone', action='store',
                        required=False, help='[1,2,3,4] or "all" without spaces', default='info')
    parser.add_argument("-s", '--start_zone', dest='start_zone', type=int, action='store',
                        required=False, help='Starting zone number', default=None)
    parser.add_argument("-e", '--end_zone', dest='end_zone', type=int, action='store',
                        required=False, help='Ending zone number', default=None)
    args = parser.parse_args()
    zones = args.zone
    start_zone = args.start_zone
    end_zone = args.end_zone

    URL = "https://www.ireps.gov.in/epsn/home/showTenderDetails.do?listType=nitLiveOpen"

    if zones == 'info':
        region_tenders_link = get_main_page_data(URL)
        for i, row in enumerate(region_tenders_link):
            print(f"# {i + 1}\t{row[0]}{' ' * (30 - len(row[0]) - len(row[1]))}{row[1]}")
        print("ENTER THE COMMAND LIKE: 'python script_name.py -z [1,2,3,4]'\n"
              "Where 1,2,3,4 are zonal numbers without space\n"
              "Enter 'python script_name.py -z all' for all zones ")
        sys.exit()
    elif zones.lower() == 'all':
        region_tenders_link = get_main_page_data(URL)
    else:
        region_tenders_link = get_main_page_data(URL)
        if '[' not in zones:
            zones = re.sub(' ', '', zones).split(',')
            zones = [int(i) - 1 for i in zones if int(i) <= len(region_tenders_link)]
        elif ',' not in zones:
            zones = re.findall('\d+', zones)[0]
            zones = [int(zones) - 1] if int(zones) <= len(region_tenders_link) else None
        else:
            zones = eval(zones)
            zones = [int(i) - 1 for i in zones if int(i) <= len(region_tenders_link)]

        if not zones:
            print("PLEASE ENTER THE VALID ZONE NUMBERS")
            region_tenders_link = get_main_page_data(URL)
            for i, row in enumerate(region_tenders_link):
                print(f"# {i + 1}\t{row[0]}{' ' * (30 - len(row[0]) - len(row[1]))}{row[1]}")
            print("ENTER THE COMMAND LIKE: 'python script_name.py -z [1,2,3,4]'\n"
                  "Where 1,2 3 & 4 are zonal numbers\n"
                  "Enter 'python script_name.py -z all' for all zones ")
            sys.exit()
        else:
            region_tenders_link = [region_tenders_link[i] for i in zones]

    if start_zone and end_zone:
        region_tenders_link = region_tenders_link[start_zone - 1:end_zone]
    else:
        region_tenders_link = region_tenders_link

    logging.info("The following railway zones are selected and are being scraped")
    print("The following railway zones are selected and are being scraped")
    for i in region_tenders_link:
        print(i[0])
        logging.info(i[0])

    total_data = []
    for r in region_tenders_link:
        zonal_data = []
        zone = r[0]
        print(r[2][4:])
        r[2] = "http" + r[2][4:]
        number_of_pages = get_number_of_pages(r[2])
        print(f"CURRENTLY SCRAPING ZONE: {zone.upper()}")
        for num in range(1, number_of_pages + 1):
            print(f"\tScraping page {num} out of {number_of_pages}")
            logging.info(f"\tScraping page {num} out of {number_of_pages}")
            URL = f"{r[2]}&pageNo={num}"
            logging.info("Current Zonal url: " + URL)
            zonal_data = get_page_data(URL, zone, zonal_data)
            time.sleep(1)

        df = pd.DataFrame(zonal_data)
        df.columns = ['Zone', 'Dept.', 'Tender No.', 'Tender Title', 'Type', 'Due Date/Time', 'Due Days',
                      'Advertised Value', 'Doc Link', 'Bidding type', 'Bidding System', 'Date Time Of Uploading Tender',
                      'Pre-Bid Conference Date Time', 'Earnest Money (Rs.)', 'Contract Type']

        if not os.path.exists('Files'):
            os.makedirs('Files')

        df.to_csv(os.path.join(os.getcwd(), 'Files', f'{zone}_{now.year}_{now.month}_{now.day}.csv'), index=False)
        print(f"{zone} data saved")
        total_data.extend(zonal_data)
        total_df = pd.DataFrame(total_data)
        total_df.columns = ['Zone', 'Dept.', 'Tender No.', 'Tender Title', 'Type', 'Due Date/Time', 'Due Days',
                            'Advertised Value', 'Doc Link', 'Bidding type', 'Bidding System',
                            'Date Time Of Uploading Tender', 'Pre-Bid Conference Date Time', 'Earnest Money (Rs.)',
                            'Contract Type']
        total_df.to_csv(os.path.join(os.getcwd(), 'Files',
                                     f'total_data_{now.year}_{now.month}_{now.day}.csv'), index=False)
