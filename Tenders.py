from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

import os
import base64
import xlsxwriter
from datetime import datetime

import re
import pytesseract
from PIL import Image
import cv2

import sys

# Accessing command-line arguments
arguments = sys.argv
script_name = arguments[0]
name = arguments[1]
url = arguments[2]
URL = url.replace('"', '')
class Extr:
    def __init__(self):
        folder_all = "Files"
        options = Options()
        options.add_argument("--headless")  # Run Chrome in headless mode (without GUI)     
        options.add_argument("--disable-gpu")  # Disable GPU usage
        options.add_argument("--log-level=3")  # Set the log level to suppress warnings

        capTextInput = ""
        while True:
            while True:
                # Initialize the ChromeDriver
                driver = webdriver.Chrome(options=options)
                driver.set_page_load_timeout(600)  # Increase the timeout to 60 seconds
                driver.implicitly_wait(10)  # Set implicit wait to 10 seconds
                print(URL)
                # sys.exit()
                driver.get(URL) # var
                
                # Extract the CAPTCHA image data and save it as an image file
                capImage = driver.find_element("xpath","//img[@id='captchaImage']")
                imgData = capImage.get_attribute('src')
                imgData = imgData[22:]
                imgData = imgData.replace('\\n', '')
                imgData = imgData.replace('\\r', '')
                imgData = imgData.replace('%0A', '')

                cap_folder_path = "CAP"  # Folder name
                cap_file_name = '' +name+ '.png'  # File name
                cap_file_path = os.path.join(cap_folder_path, cap_file_name)
                # Check if the folder exists, and create it if it doesn't
                if not os.path.exists(cap_folder_path):
                    os.makedirs(cap_folder_path)
                with open(cap_file_path, "wb") as fh:
                    fh.write(base64.b64decode(imgData))

                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                
                # Open the image
                image = Image.open(cap_file_path)

                # Convert the image to RGBA if it's not already in that mode
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')

                # Get the pixel data of the image
                pixels = image.load()

                # Define the blue color range (adjust the values if needed)
                blue_min = (0, 0, 150)  # Minimum blue color (RGB)
                blue_max = (50, 50, 255)  # Maximum blue color (RGB)

                # Iterate over each pixel and remove blue dots
                for x in range(image.width):
                    for y in range(image.height):
                        r, g, b, a = pixels[x, y]

                        # Check if the pixel falls within the blue color range
                        if blue_min[0] <= r <= blue_max[0] and \
                                blue_min[1] <= g <= blue_max[1] and \
                                blue_min[2] <= b <= blue_max[2]:
                            # Set the pixel to transparent (remove the blue dot)
                            pixels[x, y] = (r, g, b, 0)

                # Create a new RGB image with white background
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))

                # Composite the original image onto the new RGB image, preserving black text
                rgb_image.paste(image, (0, 0), mask=image)

                # Path to the CAPTCHA image
                captcha_image_path_jpg = './CAP/' + name + '_output_image.jpg'

                # Save the resulting RGB image
                rgb_image.save(captcha_image_path_jpg)  # You can change the output file format if desired

                # Load the CAPTCHA image using cv2 (OpenCV)
                image = cv2.imread(captcha_image_path_jpg)

                # Perform denoising on the image
                denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

                # Convert the denoised image to grayscale
                gray_image = cv2.cvtColor(denoised_image, cv2.COLOR_BGR2GRAY)

                # Perform OCR using pytesseract
                text = pytesseract.image_to_string(gray_image)

                extracted_text = text.strip()
                
                # Filter text to include only alphabets and numerics while removing spaces
                filtered_text = re.sub(r'[^A-Za-z0-9]', '', extracted_text)
                filtered_text = filtered_text.upper()

                if re.match(r'^[A-Z0-9]{6}$', filtered_text): # Check if any six-character string is present in filtered_text and break the loop
                    capTextInput = filtered_text
                    break
                print("CAPTCHA mismatch trying again...")
                
            print("CAPTCHA : Found /",capTextInput)
            
            try: # Fill in the search form and submit
                driver.execute_script("document.getElementById('captchaText').value='" + capTextInput + "'")
                driver.execute_script("document.getElementById('TenderType').value=1")
                driver.execute_script("document.getElementById('valueCriteria').value=4")
                driver.execute_script("document.getElementById(\"valueParameter\").value=3")
                driver.execute_script("document.getElementById('FromValue').value=99999999")
                driver.find_element("xpath", "//*[@id='submit']").click()
            except Exception as e: 
                print("An error occurred:", str(e))
            # links = len(driver.find_elements("xpath", "//a[starts-with(@id,'DirectLink_0')]"))

            links = len(driver.find_elements("xpath", "//td/a[starts-with(@id,'DirectLink_0')]"))
            # links = len(driver.find_elements((By.XPATH, "//td/a[starts-with(@id, 'DirectLink_0')]")))
            
            if links != 0:
                break  # Exit the loop if links are found successfully
            print("No links: trying again... ", links)
            
        print(name, " Tenders Scraping ... ")
        # Create an Excel workbook to store the scraped data
        b = datetime.now()
        fname = b.strftime("%d-%m-%Y %H_%M_%S")
        folder_name = name + '_Tenders'
        file_name = folder_name + '_' + fname + '.xlsx'
        file_path = os.path.join(folder_all, file_name)

        # Create the folder if it doesn't exist
        if not os.path.exists(folder_all):
            os.makedirs(folder_all)

        workbook = xlsxwriter.Workbook(file_path)
        worksheet1 = workbook.add_worksheet("ListOfTenders")

        # Write the column headers in the worksheet
        worksheet1.write(0, 0, "Organisation Chain")
        worksheet1.write(0, 1, "Tender Reference Number")
        worksheet1.write(0, 2, "Tender ID")
        worksheet1.write(0, 3, "EMD Amount in Rs")
        worksheet1.write(0, 4, "Title")
        worksheet1.write(0, 5, "Work Description")
        worksheet1.write(0, 6, "Tender Value in Rs")
        worksheet1.write(0, 7, "Pre Bid Meeting Date")
        worksheet1.write(0, 8, "Bid Submission End Date")
        worksheet1.write(0, 9,"Published Date")
        worksheet1.write(0, 10,"Tender Type")
        worksheet1.write(0, 11,"Tender Category")
        worksheet1.write(0, 12,"Tender Fee")
        worksheet1.write(0, 13,"Location")
        worksheet1.write(0, 14,"Period Of Work(Days)")
        worksheet1.write(0, 15,"Document Download / Sale End Date")
        worksheet1.write(0, 16,"URL")
        worksheet1.write(0, 17,"GET")
        # ... (write the remaining column headers)
        
        cnt = 0
        while True:
            for j in range(1, links + 1):
                print('\r' + "Tender  : " + str((cnt * 20) + j), end='')

                elements = driver.find_elements("xpath", "//a[starts-with(@id,'DirectLink_0')]")
                if j > len(elements):
                    break
                try:

                    elements[j - 1].click()
                except IndexError:
                    break
                # Extract data from the tender details page and write it to the worksheet
                orgChain = driver.find_element("xpath","//*[text()='Organisation Chain']/parent::*/following-sibling::td[1]")
                tenderRefNumber = driver.find_element("xpath","//*[text()='Tender Reference Number']/parent::*/following-sibling::td[1]")
                tenderID = driver.find_element("xpath","//*[text()='Tender ID']/parent::*/following-sibling::td[1]")
                emdAmount = driver.find_element("xpath","//*[contains(text(),'EMD Amount in ₹ ')]/following-sibling::td[1]")
                tenderTitle = driver.find_element("xpath","//*[text()='Title']/parent::*/following-sibling::td[1]")
                workDescription = driver.find_element("xpath","//*[text()='Work Description']/parent::*/following-sibling::td[1]")
                tenderValue = driver.find_element("xpath","//*[text()='Tender Value in ₹ ']/parent::*/following-sibling::td[1]")
                prebidMeetDate = driver.find_element("xpath","//*[text()='Pre Bid Meeting Date']/parent::*/following-sibling::td[1]")
                bidSubmitEndDate = driver.find_element("xpath","//*[text()='Bid Submission End Date']/parent::*/following-sibling::td[1]")
                publishedDate = driver.find_element("xpath","//*[text()='Published Date']/parent::*/following-sibling::td[1]")
                tenderType = driver.find_element("xpath","//*[contains(text(),'Tender Type')]/following-sibling::td[1]")
                tenderCat = driver.find_element("xpath","//*[contains(text(),'Tender Category')]/following-sibling::td[1]")
                try:
                    tenderFee = driver.find_element("xpath","//*[contains(text(),'Tender Fee in ₹')]/following-sibling::td[1]")
                    if tenderFee is not None:
                        tender_fee_text = tenderFee.get_attribute("innerText")
                        # Continue processing with the tender_fee_text
                    else:
                        tender_fee_text = None  # Set a default value or perform any other necessary actions
                except NoSuchElementException:
                    tender_fee_text = None  # Set a default value or perform any other necessary actions
                location = driver.find_element("xpath","//*[text()='Location']/parent::*/following-sibling::td[1]")
                periodofDays = driver.find_element("xpath","//*[text()='Period Of Work(Days)']/parent::*/following-sibling::td[1]")
                docDownloadstart = driver.find_element("xpath","//*[text()='Document Download / Sale End Date']/parent::*/following-sibling::td[1]")
                # ... (extract the remaining data fields and write them to the worksheet)
                worksheet1.write((cnt * 20)+j,0,orgChain.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,1,tenderRefNumber.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,2,tenderID.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,3,emdAmount.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,4,tenderTitle.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,5,workDescription.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,6,tenderValue.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,7,prebidMeetDate.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,8,bidSubmitEndDate.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,9,publishedDate.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,10,tenderType.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,11,tenderCat.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,12,tender_fee_text)
                worksheet1.write((cnt * 20)+j,13,location.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,14,periodofDays.get_attribute("innerText"))
                worksheet1.write((cnt * 20)+j,15,docDownloadstart.get_attribute("innerText"))
                urllabel = '' + name + '_Tenders'
                worksheet1.write((cnt * 20)+j,16, urllabel) 
                current_date = datetime.now().date() # Get the current date
                worksheet1.write((cnt * 20)+j,17,current_date.strftime("%d/%m/%Y"))
                # ... (write the remaining data to the worksheet)
                driver.find_element("xpath", "//a[@id='DirectLink_11' and text()='Back']").click()
            
            cnt += 1
            print(" P /", cnt)
            try: # Find the next page button for the next iteration
                driver.find_element(By.XPATH, ".//a[@id='linkFwd']").click()
            except NoSuchElementException:
                # print("Element not found. Handle the exception here.")
                break
            
        # Close the workbook
        workbook.close()
        
        # Close the webdriver
        # driver.quit()
        print("Exeting...")


if __name__ == "__main__":
    extr = Extr()
    
# Stop execution
sys.exit()