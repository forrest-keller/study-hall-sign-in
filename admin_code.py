##########################################################################
#                                This code is a copyright of c^2. Do not #
#                 ##             re-use, re-distribute, or re-create     # 
#               #####            any segment of this code without        #
#              ##   ##           permission from the owners of the code. #
#                  ##                                                    #
#                ##              To contact the owners of this project,  #
#      ######  ########          please contact:                         #
#   #####   ##                       - fkeller20@ssis.edu.vn             #
#  ####                              - sunkim19@ssis.edu.vn              #
# ####                               - hsekine21@ssis.edu.vn             #
# ####                               - htran19@ssis.edu.vn               #
#  ####     #                                                            #
#   #####   ##                                                           #
#      ######                                                            #
#                                                                        #
#                                                                        #
# PREREQUISITES: googleapiclient, oauth2client:                          #
# pip install --upgrade google-api-python-client oauth2client            #
##########################################################################

# Google API
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient import discovery

# Python
from datetime import datetime
from time import sleep
import os
import ConfigParser

# RFID Scanner
import RPi.GPIO as GPIO
import MFRC522
import signal

# Spreadsheet object
from user_code import Spreadsheet, readConfig, clearTerminal, getUID

def configHome():
    '''
    Configuration panel Home.
    '''
    
    clearTerminal()
    
    print("CONFIGURATION PANEL\n\n1: Change spreadsheet ID\n2: Change queries\n3: Register ID card\n4: Apply Changes and Exit Configuration\n\n")
    
    while True:
        selection = raw_input("Enter selection: ")
        
        if selection in ['1', '2', '3', '4']:
            return selection
        else:
            print("Invalid Selection")


def changeSpreadsheetURL():
    '''
    Asks user for new ID, and writes to config file.
    '''
    
    clearTerminal()
    print("CONFIGURATION PANEL>SPREADSHEET URL\n\n")
    selection = raw_input("Enter new spreadsheet ID: ")
    
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')
    
    config.set('main', 'spreadsheet_id', selection)
    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    
    
def changeQueries():
    '''
    Displays queries, and prompts to add or remove queries, or go back.
    '''
    
    # Ask and enter query
    while True:
        # Header
        clearTerminal()
        print("CONFIGURATION PANEL>CHANGE QUERIES\n\n1: Add new query\n2: remove query\n3: back\n\n")
        
        # Print current queries
        print("Current Queries: ")
        config = ConfigParser.RawConfigParser()
        config.read('config.ini')
        queries = config.get('main', 'queries')
        queries = queries.split('//')
        
        if len(queries) > 0:
            for i in range(0, len(queries)):
                print('    ' + str(i + 1) + ') ' + queries[i])
    
        print("\n\n")
        selection = raw_input("Enter selection: ")
        
        if selection == '1':
            newQuery()
        elif selection == '2':
            deleteQuery()
        elif selection == '3':
            break
        else:
            print("Invalid Selection")

def newQuery():
    '''
    Asks for a question, and adds it to the config file. 
    '''
    
    clearTerminal()
    
    print("CONFIGURATION PANEL>CHANGE QUERIES>ADD QUERY\n\n")
    
    selection = raw_input("Please enter question to add: ")
    
    # Enter query into config file
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')
    queries = config.get('main', 'queries')
    queries = queries + '//' + selection
    
    config.set('main', 'queries', queries)
    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    
    
def deleteQuery():
    '''
    Shows all current queries, and prompts for query to remove.
    '''
    
    # Init
    clearTerminal()
    print("CONFIGURATION PANEL>CHANGE QUERIES>REMOVE QUERY\n\n")
    
    # Get current queries
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')
    queries = config.get('main', 'queries')
    queries = queries.split('//')
    
    for i in range(0, len(queries)):
        print(str(i + 1) + ': ' + queries[i])
    print('\n\n')
    
    # Get query to remove
    while True:
        selection = raw_input("Enter query to remove: ")
        if len(queries) + 1 > int(selection) > 0:
            break
        else:
            print("Invalid Selection")
    
    # Remove query from config file
    del queries[int(selection) - 1]
    queries = '//'.join(queries)
    
    config.set('main', 'queries', queries)
    
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def registerCard(spreadsheet):
    '''
    Registers card. Asks for Name & Grade, and writes user to the bottom most row of current sheet.
    '''
    
    clearTerminal()
    print("CONFIGURATION PANEL>REGISTER ID CARD\n\n")
    
    append_values = []
    
    while True:
        print('Scan the ID card you want to register')
        uid = getUID()
        name = raw_input("Enter name associated with card: ")
        grade = raw_input("Enter grade associated with card: ")
        
        append_values.append([name, grade, uid])
        
        end = raw_input("Would you like to add more ID cards? (yes or no): ")
        
        if end == 'n' or end == 'no':
            break
        print('\n')
    
    current_sheet = spreadsheet.read('Configuration!B1')[0][0]
    registered_people_length = len(spreadsheet.read(current_sheet + '!A:A'))
    
    for i in range(len(append_values)):
        spreadsheet.write((current_sheet + '!A' + str(registered_people_length + 1)), append_values[i])
        registered_people_length += 1
    
    

def applyChanges(spreadsheet):
    '''
    Reads config file, and changes spreadsheet headers to conform to query requests
    '''
    
    clearTerminal()
    print("Loading settings onto google sheet...")
    
    # get queries
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')
    queries = config.get('main', 'queries')
    queries = queries.split('//')
    
    header = queries
    header.append('Signed in')
    header.append('Time')
    
    current_block = spreadsheet.read('Configuration!B1')[0][0]
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    spreadsheet.write(current_block + '!E1', header)
    spreadsheet.clear(current_block + '!' + alphabet[len(header) + 4] + '1:Z')

def main():
    '''
    Creats the configuration panel.
    '''
    
    # Initialize
    config_values = readConfig('config.ini')
    
    number_of_queries = config_values[5]
    column_queries = config_values[6]
    queries = str(config_values[7]).split('//')
    
    spreadsheet = Spreadsheet(
        scope = config_values[0],
        spreadsheet_id = config_values[1],
        
        column_name = config_values[2],
        column_scan_value = config_values[3],
        column_required_action = config_values[4],
        
        number_of_queries = number_of_queries,
        column_queries = column_queries,
        
        
        header_length = config_values[8]
    )
    
    # Check if admin user has admin card
    print('Please scan admin card.')
    
    user_uid = getUID()
    print('Verifying ID card.')
    admin_uid = spreadsheet.read('Configuration!B4')[0][0]
    
    if user_uid == admin_uid:
        while True:
            selection = configHome()
            if selection == '1':
               changeSpreadsheetURL()
            elif selection == '2':
                changeQueries()
            elif selection == '3':
                registerCard(spreadsheet)
            elif selection == '4':
                applyChanges(spreadsheet)
                break
    else:
        print('Acess denied.')
        sleep(2)
        
        
   
# --MAIN-- #

if __name__ == '__main__':
    main()
    