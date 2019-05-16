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

class Spreadsheet(object):
    '''
    Scanner object that can read, write, and clear given spreadsheet.
    '''
    
    def __init__(self, scope, spreadsheet_id, column_name,
                 column_scan_value, column_required_action, 
                 number_of_queries, column_queries, header_length):
        
        # Spreadsheet data
        self.scope = scope
        self.spreadsheet_id = spreadsheet_id
        self.credentials = self.generateCredentials()
        self.service = discovery.build('sheets', 'v4', credentials=self.credentials)
        
        # Column data
        self.column_name = column_name
        self.column_scan_value = column_scan_value
        self.column_required_action = column_required_action
        
        # Query data
        self.number_of_queries = number_of_queries
        self.column_queries = column_queries
        
        # Header length
        self.header_length = header_length
        
    
    def read(self, _range):
        '''
        Returns a list of values, given a range of cells to read.
        '''
        
        result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=_range).execute()

        return result.get('values', [])

        
    def write(self, _range, values_to_write):
        '''
        Writes a cell range with values.
        '''
        
        value_input_option = 'RAW'
        value_range_body = {
          "range": _range,
          "values": [values_to_write]
        }

        request = self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=_range, valueInputOption=value_input_option, body=value_range_body)
        response = request.execute()
        
        
    def clear(self, _range):
        '''
        Clears a given cell range.
        '''
        
        batch_clear_values_request_body = {
            'ranges': [_range],
        }
        
        request = self.service.spreadsheets().values().batchClear(spreadsheetId=self.spreadsheet_id, body=batch_clear_values_request_body)
        response = request.execute()
    
    def generateCredentials(self):
        '''
        Returns credentials, as to be used un the Spreadsheet object.
        '''
        store = file.Storage('token.json')
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', self.scope)
            credentials = tools.run_flow(flow, store)

        return credentials


def readConfig(file_name):
    '''
    Reads a config file.
    '''
    
    # Open and read file.
    config = ConfigParser.ConfigParser()
    config.read(file_name)
    
    # Get variables
    scope = config.get('main', 'scope')
    spreadsheet_id = config.get('main', 'spreadsheet_id')

    column_name = config.get('main', 'column_name')
    column_scan_value = config.get('main', 'column_scan_value')
    column_required_action = config.get('main', 'column_required_action')
    
    number_of_queries =config.get('main', 'number_of_queries')
    column_queries = config.get('main', 'column_queries')
    queries = config.get('main', 'queries')
    
    header_length = config.get('main', 'header_length')
    
    # Return list of variables.
    return [scope, spreadsheet_id, column_name, column_scan_value, column_required_action, number_of_queries, column_queries, queries, header_length]


def clearTerminal():
    '''
    Clears the terminal window.
    '''
    
    os.system('cls' if os.name == 'nt' else 'clear')


def getUID():
    '''
    Returns the UID of scanned card.
    '''

    # Hook the SIGINT
    # signal.signal(signal.SIGINT, end_read)
    
    # Create an object of the class MFRC522
    MIFAREReader = MFRC522.MFRC522()
    
    # This loop keeps checking for chips. If one is near it will get the UID and authenticate
    while True:
        
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()
        
        if status == MIFAREReader.MI_OK:
            GPIO.cleanup()
            return ''.join([str(element) for element in uid])
    
    

def main():
    '''
    Main function. Runs code forever untill quit.
    '''
    
    # Welcome message
    clearTerminal()
    print("Welcome to this sign in system.")
    print("Loading spreadsheet...")
    
    # Initialize
    config_values = readConfig('config.ini')
    
    # Get questions
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
    
    # Run main code
    while True:
        
        current_sheet = spreadsheet.read('Configuration!B1')[0][0]
        
        clearTerminal()
        
        # Get card uid
        print("Please scan ID card.")
        rfid_uid = getUID()
        clearTerminal()
        
        print("Scanning ID card...")
        
        all_rfid_uid = spreadsheet.read(current_sheet + '!' + spreadsheet.column_scan_value + str(int(spreadsheet.header_length) + 1) + ':' + spreadsheet.column_scan_value)
        all_rfid_uid = [str(all_rfid_uid[i][0]) for i in range(len(all_rfid_uid))]
        
        if rfid_uid in all_rfid_uid:
            uid_row = all_rfid_uid.index(rfid_uid) + int(spreadsheet.header_length) + 1
            
            required_action = spreadsheet.read(current_sheet + '!' + spreadsheet.column_required_action + str(uid_row))
            
            if required_action == []:
                # Ask queries
                
                responses = []
                
                for i in range(len(queries)):
                    responses.append(raw_input(queries[i]))
                
                # ONLY FOR STUDY HALL SIGN IN. NOT PART OF NORMAL CODE.
                # If nothing is entered, default to library.
                if responses[0] == '':
                    responses[0] = 'Library'
                
                responses.append('YES')
                responses.append(datetime.now().strftime('%Y-%m-%d %H:%M'))
                
                # Report results NOTE: THIS IS NOT GOOD. ONLY SPESCIFIC TO STUDY HALL SIGN IN.
                spreadsheet.write(str(current_sheet) + '!' + str(spreadsheet. column_queries) + str(uid_row), responses)
                
                print("You are signed in.")
            else:
                print("Required Action: " + required_action[0][0])
                
                try:
                    confirmed = input("Press any button to continue.")
                except:
                    print("You are NOT signed in. Please see Mr.Le.")
                    sleep(1)
            
        else:
            print('Unregistered ID card.')

# --MAIN-- #

if __name__ == '__main__':
    main()
    