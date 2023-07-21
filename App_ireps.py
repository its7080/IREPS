# -*- coding: utf-8 -*-
import subprocess
import os
import sys

mobile_no = input("Enter 10 digit Mobile No: ")

def run_script_in_command_prompt(name, url):
    print(name, url)
    # sys.exit()
    subprocess.Popen(['start', 'cmd', '/k', 'python', 'tender_ireps.py', name, url, mobile_no], shell=True)

def clear_screen():
    if os.name == 'nt':  # for Windows
        os.system('cls')
    else:  # for Unix-based systems
        os.system('clear')

# Specify the paths of the scripts, names, and URLs
scripts = [('11', 'CONTAINER CORPORATION OF INDIA LTD'),
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

def display_menu():
    clear_screen()
    print("Choose an option:")
    print("1. Run all scripts")
    print("2. Select scripts to run")
    print("0. Exit")

while True:
    display_menu()

    option = input("Enter your choice: ")

    if option == '1':
        clear_screen()
        # Run all scripts in a separate command prompt window
        for name, url in scripts:
            run_script_in_command_prompt(name, url)
    elif option == '2':
        while True:
            clear_screen()
            print("Select scripts to run:")
            for i, (name, url) in enumerate(scripts):
                print(f"{i+1}. - {url}")
            print("0. Back to the main menu")

            selected_scripts = input("Enter script numbers (comma-separated): ").split(',')

            if '0' in selected_scripts:
                break

            for script_number in selected_scripts:
                script_number = int(script_number.strip())
                if script_number > 0 and script_number <= len(scripts):
                    name, url = scripts[script_number - 1]
                    run_script_in_command_prompt(name, url)
                else:
                    print("Invalid script number.")
    elif option == '0':
        break
    else:
        print("Invalid option. Please try again.")
        input("Press Enter to continue...")
