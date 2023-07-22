# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import sys
import requests
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium.common.exceptions import NoAlertPresentException
import os
import pdfplumber
import xlsxwriter
import subprocess
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import urllib.request
from requests.exceptions import Timeout, RequestException
# Accessing command-line arguments
# arguments = sys.argv
# script_name = arguments[0]
# org_id = arguments[1]
# org_name = arguments[2]
# mobile_no = arguments[3]

# Start the WebDriver service
service = Service(ChromeDriverManager().install())
service.start()

# Configure Chrome options
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')  # Maximize the Chrome window
options.add_argument('--headless=new')
options.add_argument("--disable-gpu")
options.add_argument("--log-level=3")
# options.add_experimental_option('prefs', {
#     'plugins.always_open_pdf_externally': True,
#     'download.default_directory': 'path/to/save/downloads',
#     'download.prompt_for_download': False,
#     'download.directory_upgrade': True,
#     'safebrowsing.enabled': True
# })

# Launch Chrome
driver = webdriver.Chrome(service=service, options=options)

# Open the URL
url = "https://www.ireps.gov.in/epsn/anonymSearch.do"
driver.get(url)

print("Welcome to the IREPS Scraping system!")


def getcap():
    # Find the <img> element with the src attribute containing "Captcha.jpg"
    captcha_image = driver.find_element(By.CSS_SELECTOR, 'img[src*="Captcha.jpg"]')

    # Get the source URL of the image
    captcha_image_url = captcha_image.get_attribute("src")

    # Download the image
    response = requests.get(captcha_image_url, stream=True)
    if response.status_code == 200:
        with open("Captcha.jpg", "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

    # Open the downloaded Captcha image using PIL
    # captcha_image = Image.open("Captcha.jpg")
    # Initialize the WebDriver
    # Get the current directory
    # Path to the captcha image file
    # Path to the captcha image file
    captcha_file_path = "Captcha.jpg"

    # Open the image file using the default image viewer
    subprocess.Popen([captcha_file_path], shell=True)

    # Get the verification code from the user
    Verification_code = input("Enter The Verification Code : ")

    # Close the window using the taskkill command
    subprocess.Popen(['taskkill', '/F', '/IM', 'PhotosApp.exe'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Remove the temporary image file
    os.remove(captcha_file_path)


    return Verification_code

def getotp(mobile_no):
    Verification_code = getcap()
    # mobile_no = input("Enter 10 digit Mobile No: ")
    driver.execute_script("document.getElementById('mobileNo').value='" + mobile_no + "'")

    driver.execute_script("document.getElementById('verification').value='" + Verification_code + "'")

    driver.find_element("xpath", "//input[@value='Get OTP']").click()
    # time.sleep(1)

    # Check if the alert is present
    try:
        alert = driver.switch_to.alert
    except NoAlertPresentException:
        print("No alert present")
        return None
    if alert.text == "Maximum OTP limit exceeded.":
        # If the alert message matches the expected text, accept the alert
        alert.accept()
        print("OTP limit exceeded. Alert accepted.")
        print("Use existing OTP")
    else:
        # Handle other alerts or exceptions
        print("Unexpected alert:", alert.text)
    print("OTP generated check your message box")
    return Verification_code

def save_pdf(pdf_url, script_name):
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()  # Raise an exception if the response status code indicates an error
        pdf_content = response.content
        with open(f'{script_name}.pdf', 'wb') as f:
            f.write(pdf_content)
        # print(f"PDF for {org_name} downloaded successfully.")
    except Timeout:
        print("Connection timeout. Unable to download the PDF.")
    except RequestException as e:
        print(f"Error occurred during the request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def getpdfdata(script_name):
    time.sleep(1)
    with pdfplumber.open(f'{script_name}.pdf') as pdf:
        table = pdf.pages[0].extract_tables()[0]

    table = [[value for value in sublist if value is not None] for sublist in table]

    new_table = [row[i*2:i*2+2] for row in table for i in range(len(row) // 2)] + [row for row in table if len(row) <= 2]

    extracted_info = {}
    keys_to_extract = ['Name of Work', 'Bidding type', 'Tender Type', 'Bidding System', 'Tender Closing Date Time', 'Date Time Of Uploading Tender', 'Pre-Bid Conference Date Time', 'Advertised Value', 'Earnest Money (Rs.)', 'Contract Type']

    for item in new_table:
        if item[0] in keys_to_extract and len(item) > 1:
            extracted_info[item[0]] = item[1]

    name_of_work = extracted_info.get('Name of Work', '')
    bidding_type = extracted_info.get('Bidding type', '')
    tender_type = extracted_info.get('Tender Type', '')
    bidding_system = extracted_info.get('Bidding System', '')
    tender_closing_date_time = extracted_info.get('Tender Closing Date Time', '')
    date_time_of_uploading_tender = extracted_info.get('Date Time Of Uploading Tender', '')
    pre_bid_conference_date_time = extracted_info.get('Pre-Bid Conference Date Time', '')
    advertised_value = extracted_info.get('Advertised Value', '')
    earnest_money = extracted_info.get('Earnest Money (Rs.)', '')
    contract_type = extracted_info.get('Contract Type', '')

    return name_of_work, bidding_type, tender_type, bidding_system, tender_closing_date_time, date_time_of_uploading_tender, pre_bid_conference_date_time, advertised_value, earnest_money, contract_type


def __drill(worksheet1,cnt,value,script_number,script_name):
    # print("i = ", i)
    # print(no_of_pages)

    # print("ik = ",k)
    #Perform your desired actions for each page here
    # filtered_a_tags = [a_tag for a_tag in a_tags if a_tag.find_elements(By.XPATH, './/img[@title="View Tender Details"]')]
    # time.sleep(1)
    a_tags = driver.find_elements(By.CSS_SELECTOR, "a[onclick]")
    filtered_a_tags = [tag for tag in a_tags if 'postRequestNewWindow(\'/epsn/nitViewAnonyms/rfq/nitPublish.do?' in tag.get_attribute('onclick')]
    # links = len(filtered_a_tags)
    # print("\nNo. of tenders in current page", links)
    # for tag in filtered_a_tags:
    #     print(tag.get_attribute('outerHTML'))
    #     print("\n")
    #     print("\n")



    # For each a tag, click on it and open the tender details page in a new window.

    # while True:
    k = 1
    for a_tag in filtered_a_tags:
        print('\r' + "Tender  : " + str((cnt * 25) + k), end='')
        a_tag.click()

        # Get the list of all the window handles.
        handles = driver.window_handles

        # Switch to the popup window.
        driver.switch_to.window(handles[1])

        tender_no = None
        dept_rly = None
        timeout = 30  # Set a timeout in seconds (adjust as needed)
        start_time = time.time()

        while tender_no is None or dept_rly is None:
            # Check for Tender No.
            # time.sleep(3)
            td_tags = driver.find_elements(By.XPATH, '//td[contains(text(), "Tender No:")]')
            if td_tags:
                tender_no = td_tags[0].find_element(By.XPATH, "following-sibling::td[1]").text

            # Check for Dept/Rly.
            # time.sleep(1)
            td_tags2 = driver.find_elements(By.XPATH, '//td[contains(text(), "Dept/Rly:")]')
            if td_tags2:
                dept_rly = td_tags2[0].find_element(By.XPATH, "following-sibling::td[1]").text

            # If both values are found or timeout is reached, break the loop.
            if tender_no is not None and dept_rly is not None:
                break

            if time.time() - start_time >= timeout:
                print("Timeout: Value not found within the specified time. Tender No and Dept/Rly")
                break

        # tender_no = None
        # dept_rly = None

        # td_tags = driver.find_elements(By.XPATH, '//td[contains(text(), "Tender No:")]')
        # if td_tags:
        #     tender_no = td_tags[0].find_element(By.XPATH, "following-sibling::td[1]").text
        #     # print("Tender No: ", tender_no)
        # else:
        #     print("Tender No: not found.")

        # td_tags2 = driver.find_elements(By.XPATH, '//td[contains(text(), "Dept/Rly:")]')
        # if td_tags2:
        #     dept_rly = td_tags2[0].find_element(By.XPATH, "following-sibling::td[1]").text
        #     # print("Dept/Rly: ", dept_rly)
        # else:
        #     print("Dept/Rly: not found.")
        
        # Wait for the anchor tag containing the specified text to be clickable
        
        wait = WebDriverWait(driver, 10)
        # Use XPath to locate the element based on its attributes
        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Download Tender Doc. (Pdf)')]")))


        # Click on the anchor tag to trigger the function
        download_button.click()
        # time.sleep(1)
        handles2 = driver.window_handles
        driver.switch_to.window(handles2[2])

        pdf_url = driver.current_url

        save_pdf(pdf_url, script_name)
        # time.sleep(1)
        name_of_work, bidding_type, tender_type, bidding_system, tender_closing_date_time, date_time_of_uploading_tender, pre_bid_conference_date_time, advertised_value, earnest_money, contract_type = getpdfdata(script_name)
        try:
            closing_datetime = datetime.strptime(tender_closing_date_time, '%d/%m/%Y %H:%M')
            uploading_datetime = datetime.strptime(date_time_of_uploading_tender, '%d/%m/%Y %H:%M')
            due_days = (closing_datetime - uploading_datetime).days
        except ValueError as e:
            # Exception occurred (e.g., invalid date format or empty string)
            due_days = None
        # print(pdf_url)
        # print(xl)
        worksheet1.write((cnt * 25)+k,0,value)
        worksheet1.write((cnt * 25)+k,1,dept_rly)
        worksheet1.write((cnt * 25)+k,2,tender_no)
        worksheet1.write((cnt * 25)+k,3,name_of_work)
        worksheet1.write((cnt * 25)+k,4,tender_type)
        worksheet1.write((cnt * 25)+k,5,tender_closing_date_time)
        worksheet1.write((cnt * 25)+k,6,due_days)
        worksheet1.write((cnt * 25)+k,7,advertised_value)
        worksheet1.write((cnt * 25)+k,8,pdf_url)
        worksheet1.write((cnt * 25)+k,9,bidding_type)
        worksheet1.write((cnt * 25)+k,10,bidding_system)
        worksheet1.write((cnt * 25)+k,11,date_time_of_uploading_tender)
        worksheet1.write((cnt * 25)+k,12,pre_bid_conference_date_time)
        worksheet1.write((cnt * 25)+k,13,earnest_money)
        worksheet1.write((cnt * 25)+k,14,contract_type)



        driver.close()

        # # Close the popup window.
        driver.switch_to.window(handles[1])
        driver.close()

        # Switch back to the main window.
        driver.switch_to.window(handles[0])

        k=k+1

def store_options_in_dictionary(driver):
  time.sleep(2)
  """Stores all options in a dictionary."""
  railway_zone_dropdown = Select(driver.find_element(By.XPATH, "//*[@id='railwayZone']"))
#   print(railway_zone_dropdown)
  options = railway_zone_dropdown.options
#   print(options)

  option_dict = {}
  for option in options:
    value = option.get_attribute("value")
    # print("value = ",value)
    # time.sleep(10)
    text = option.get_attribute("innerText")
    option_dict[value] = text
  return option_dict
def login(mobile_no):
    driver.refresh()
    # time.sleep(1)
    ver_code = getcap()

    # mobile_no = input("Enter 10 digit Mobile No: ")
    otp_text = input("Enter The OTP: ")
    driver.execute_script("document.getElementById('mobileNo').value='" + mobile_no + "'")

    driver.execute_script("document.getElementById('verification').value='" + ver_code + "'")

    driver.execute_script("document.getElementById('otp').value='" + otp_text + "'")

    driver.find_element("xpath", "//input[@value='Proceed']").click()
    # time.sleep(1)
    driver.find_element("xpath", "//input[@value='Custom Search']").click()
    return driver

def tender(driver, script_number, script_name):

    # driver.refresh()
    # # time.sleep(1)
    # ver_code = getcap()

    # # mobile_no = input("Enter 10 digit Mobile No: ")
    # otp_text = input("Enter The OTP: ")
    # driver.execute_script("document.getElementById('mobileNo').value='" + mobile_no + "'")

    # driver.execute_script("document.getElementById('verification').value='" + ver_code + "'")

    # driver.execute_script("document.getElementById('otp').value='" + otp_text + "'")

    # driver.find_element("xpath", "//input[@value='Proceed']").click()
    # # time.sleep(1)
    # driver.find_element("xpath", "//input[@value='Custom Search']").click()
    # time.sleep(1)
    # try:
    #     # Find all elements containing the text 'No Results Found'
    #     elements = driver.find_element(By.XPATH, f"//b[text()='No Results Found']")

    #     # Check if the elements are found and break the loop
    #     if elements:
    #         print("Found 'No Results Found'. Breaking the loop.")
    #     else:
    #         print("Continuing...")

    # except:
    # driver.execute_script("document.getElementById('organization').value='"+ org_id +"'")
    # Locate the dropdown element using an appropriate selector
    dropdown_element = driver.find_element(By.ID, 'organization')  # Replace with the actual ID of the dropdown element

    # Create a Select object and interact with the dropdown
    select = Select(dropdown_element)

    # Select option by visible text
    # select.select_by_visible_text('Option Text')

    # Select option by value
    select.select_by_value(script_number)

    # time.sleep(1)

    # # Find the select element by ID, name, class, or XPath
    # select_element = driver.find_element(By.ID, "railwayZone")  # Replace "railwayZone" with the actual ID of your select element

    # # Get all the options within the select element
    # options = select_element.find_elements(By.TAG_NAME, "option")
    # print("option",options[0])
    # time.sleep(1)
    # Create an empty dictionary to store the key-value pairs
    options_dict = store_options_in_dictionary(driver)
    # Extract the options and values
    # for option in options:
    #     value = option.get_attribute("value")
    #     text = option.text
    #     options_dict[value] = text
    # Print the options dictionary
    print("------- ZONE LIST -------")
    for value in options_dict.values():
        if value == "ALL" or value == "---Select---" or value == "All" or value == "IREPS-TESTING" or value == "IREPS-TESTING2":
            continue  # Skip the current iteration and move to the next one
        print(value)
    # time.sleep(1)
    # sys.exit()
    # Iterate through all keys in options_dict and print key-value pairs
    for key, value in options_dict.items():
        if value == "ALL" or value == "---Select---" or value == "All" or value == "IREPS-TESTING" or value == "IREPS-TESTING2":
            continue  # Skip the current iteration and move to the next one or value == "Banaras Locomotive Works" or value == "COFMOW"
        # print(f"\nKey: {key}")
        print(f"\nScraping -> {value}")
        print("-----------")
        # print(type(org_id))
        # print(type(key))
        # time.sleep(1)
        driver.execute_script("document.getElementById('organization').value='"+ script_number +"'")
        driver.execute_script("document.getElementById('workArea').value='WT'")
        driver.execute_script("document.getElementById('railwayZone').value='"+ key +"'")
        driver.execute_script("document.getElementById('tenderType').value=2")
        driver.execute_script("document.getElementById('tenderStage').value=1")
        # driver.execute_script("document.getElementByName('selectDate').value='Tender Closing Date'")
        script = """
        var selectElement = document.getElementsByName("selectDate")[0];
        for (var i = 0; i < selectElement.options.length; i++) {
            if (selectElement.options[i].textContent === "Tender Closing Date") {
                selectElement.selectedIndex = i;
                break;
            }
        }
        """
        driver.execute_script(script)
        # Get the current date
        current_date = datetime.now()
        # Add four months to the current date
        four_months_later = current_date + relativedelta(months=4)
        # Format the date as a string (optional)
        formatted_date = four_months_later.strftime("%d/%m/%Y")
        driver.execute_script("document.getElementById('ddmmyyDateformat2').value='" + formatted_date + "'")
        # time.sleep(3)
        driver.find_element("xpath", "//input[@value='Show Results']").click()
        # time.sleep(1)

        # # Find all elements containing the text 'No Results Found'
        # elements = driver.find_element(By.XPATH, f"//b[text()='No Results Found']")

        # # Check if the elements are found and break the loop
        # if elements:
        #     print("Found 'No Results Found'. Breaking the loop.")
        # else:
        #     print("Continuing...")



        # Create the folder if it doesn't exist
        if not os.path.exists(script_name):
            os.makedirs(script_name)

        # Create an Excel workbook to store the scraped data
        b = datetime.now()
        fname = b.strftime("%d-%m-%Y %H_%M_%S")

        file_name = value + '_' + fname + '.xlsx'
        file_path = os.path.join(script_name, file_name)

        workbook = xlsxwriter.Workbook(file_path)
        worksheet1 = workbook.add_worksheet("ListOfTenders")

        # Write the column headers in the worksheet
        worksheet1.write(0, 0, "Zone")
        worksheet1.write(0, 1, "Dept.")
        worksheet1.write(0, 2, "Tender No.")
        worksheet1.write(0, 3, "Tender Title")
        worksheet1.write(0, 4, "Type")
        worksheet1.write(0, 5, "Due Date/Time")
        worksheet1.write(0, 6, "Due Days")
        worksheet1.write(0, 7, "Advertised Value")
        worksheet1.write(0, 8, "Doc Link")
        worksheet1.write(0, 9,"Bidding type")
        worksheet1.write(0, 10,"Bidding System")
        worksheet1.write(0, 11,"Date Time Of Uploading Tender")
        worksheet1.write(0, 12,"Pre-Bid Conference Date Time")
        worksheet1.write(0, 13,"Earnest Money (Rs.)")
        worksheet1.write(0, 14,"Contract Type")

        cnt = 0
        i = 1
        while i <= 1000:
            print("\nPage = ", i)
            xpath_expression = f"//a[text()='{i}']"

            try:
                element = driver.find_element(By.XPATH, xpath_expression)
                element.click()
            except Exception as e:
                # Handle specific exceptions here
                if i == 1:
                    __drill(worksheet1, cnt, value, script_number, script_name)
                break
            __drill(worksheet1, cnt, value, script_number, script_name)
            if i % 10 == 0:
                print("\n\n")
                next_btn = f"//a[font[text()='next']]"
                # time.sleep(1)
                try:
                    element = driver.find_element(By.XPATH, next_btn)
                    element.click()
                except NoSuchElementException:
                    print(f"Element with text 'next' not found")
                    break
            i += 1
            cnt += 1

        # Close the workbook
        print("\nZone data Saved.\n\n")
        workbook.close()




scripts = [('12', 'BRAITHWAITE AND CO. LIMITED'),
           ('11', 'CONTAINER CORPORATION OF INDIA LTD'),
           ('05', 'CRIS'),
           ('08', 'DFCCIL'),
           ('03', 'DMRC'),
           ('17', 'INDIAN RAILWAY FINANCE CORPORATION'),
           ('15', 'IRCON INTERNATIONAL LIMITED'),
           ('01', 'Indian Railway'),
           ('09', 'KERALA RAIL DEVELOPMENT CORPORATION LTD'),
           ('18', 'KOLKATA METRO RAIL CORPORATION LTD'),
           ('02', 'KRCL'),
           ('04', 'MRVC'),
           ('10', 'RAIL VIKAS NIGAM LIMITED'),
           ('07', 'RAILTEL'),
           ('06', 'RITES Limited')]

def clear_screen():
    # Function to clear the terminal screen based on the OS.
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu():
    clear_screen()
    print("Choose an option:")
    print("1. Run all scripts")
    print("2. Select scripts to run")
    print("0. Exit")

def run_all_scripts(driver):
    for script in scripts:
        script_number, script_name = script
        print(f"Running script {script_number}: {script_name}")
        tender(driver, script_number, script_name)

def select_scripts_to_run(driver):
    print("Select scripts to run:")
    for i, script in enumerate(scripts, 1):
        script_number, script_name = script
        print(f"{i}. {script_number}: {script_name}")

    selected_scripts = input("Enter the numbers of the scripts to run (comma-separated): ").split(",")
    selected_scripts = [int(s) for s in selected_scripts]

    for num in selected_scripts:
        if 1 <= num <= len(scripts):
            script_number, script_name = scripts[num - 1]
            print(f"Running script {script_number}: {script_name}")
            tender(driver, script_number, script_name)
        else:
            print(f"Invalid script number: {num}")



def main():
    mobile_no = input("Enter 10 digit Mobile No: ")
    while True:
        print("\n1. Login")
        print("2. Generate OTP")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            driver = login(mobile_no)
            while True:
                display_menu()
                choice = input("Enter your choice: ")
                if choice == '1':
                    clear_screen()
                    run_all_scripts(driver)
                elif choice == '2':
                    clear_screen()
                    select_scripts_to_run(driver)
                elif choice == '0':
                    print("Exiting...")
                    break
                else:
                    print("Invalid choice. Please try again.")
            break
        elif choice == "2":
            getotp(mobile_no)
        elif choice == "3":
            break
        else:
            print("Invalid choice!")

    driver.quit()

# Call the main function to start the program
if __name__ == "__main__":

    def is_internet_available():
        try:
            urllib.request.urlopen('https://www.ireps.gov.in/epsn/guestLogin.do', timeout=5)
            return True
        except urllib.error.URLError:
            return False

    # Usage
    if is_internet_available():
        # Your network-related operations can be performed here
        # print("Internet connection is available. Proceed with network operations.")
        main()
    else:
        print("https://www.ireps.gov.in/epsn/guestLogin.do - Can't connect to URL. Please check your internet connection and try again.")

    
