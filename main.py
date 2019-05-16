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

import user_code
import admin_code

def main():
    '''
    Main program. Either forks to the user_code, or admin_code
    '''
    
    while True:
        user_code.clearTerminal()  
        print("Welcome to this sign in system.\n\n1: Run scanner \n2: Run configuration\n\n")
        
        selection = raw_input("Enter choice: ")
        
        if selection == '1':
            user_code.main()
        elif selection == '2':
            admin_code.main()
        else:
            print("Invalid Selection")


# --Main-- #
if __name__ == '__main__':
    main()