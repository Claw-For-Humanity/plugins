import gspread
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import time

class bucket:
  creds = None
  gc = None
  sh = None
  worksheet = None


class initializer:
    '''initialize the serverCom plugin'''
    SCOPES = ['https://www.googleapis.com/auth/drive'] 
    PATH_SERVICE_ACCOUNT_FILE = None
    PATH_CAPTURED_IMAGES = None
    ID_PARENT_SPREADSHEET = None
    ID_PARENT_CIRCULARNET_DRIVE = None
    ID_PARENT_ARCHER_DRIVE = None


    def __init__(DEFAULT_PATH, identity, spreadsheet_url, cn_drive_url, ac_drive_url):
        ''' make sure to create ".creds" & ".imgs" folder on your base folder and put the cred json file into it.
        example is
        (default_base_folder, "cfh-hawkeye-xxxxxx", "xxxxxx (end of the spreadsheet addy)", "xxxxxx (end of the drive addy)")'''
        if not os.path.exists(os.path.join(DEFAULT_PATH, '.creds')):
           print('')
        initializer.PATH_SERVICE_ACCOUNT_FILE = os.path.join(DEFAULT_PATH, '.creds', f'{identity}.json')
        initializer.PATH_CAPTURED_IMAGES = os.path.join(DEFAULT_PATH, '.imgs') 
        initializer.ID_PARENT_SPREADSHEET = spreadsheet_url
        initializer.ID_PARENT_CIRCULARNET_DRIVE = cn_drive_url
        initializer.ID_PARENT_ARCHER_DRIVE = ac_drive_url
        

        # define creds and authenticate
        bucket.creds = initializer.authenticate()
        bucket.gc = gspread.authorize(bucket.creds)
        
        # serverLog
        bucket.sh = bucket.gc.open('serverLog') # TODO: open_by_key is an alternative for this
        bucket.worksheet = bucket.gc.open('serverLog').sheet1


    def authenticate():
        creds = service_account.Credentials.from_service_account_file(initializer.PATH_SERVICE_ACCOUNT_FILE, scopes = initializer.SCOPES)
        return creds


class drive_manager:
    '''This class is specifically for uploading images on google drive.'''
    def upload_photo(bckt_type, image_name, upload_name = None):
        '''make sure to include format of the file as well i.e.) .png '''
        if type(upload_name) == type(None):
           upload_name = image_name
        if initializer.PATH_CAPTURED_IMAGES == None or initializer.PATH_SERVICE_ACCOUNT_FILE == None or bucket.creds == None:
            print("initialize first!")
            print(f"[LOG] : {initializer.PATH_CAPTURED_IMAGES}")
            print(f"[LOG] : {initializer.PATH_SERVICE_ACCOUNT_FILE}")
            print(f"[LOG] : {bucket.creds}")
            
            exit()
        
        service = build('drive', 'v3', credentials=bucket.creds)
        if bckt_type == 'cn':
          file_metadata = {
              'name':f"{upload_name}",
              'parents': [initializer.ID_PARENT_CIRCULARNET_DRIVE]
          }

        elif bckt_type == 'ac':
           file_metadata = {
              'name':f"{upload_name}",
              'parents': [initializer.ID_PARENT_ARCHER_DRIVE]
          }
           
        else:
           print('invalid type')
           return
        file_path = os.path.join(initializer.PATH_CAPTURED_IMAGES, f'{image_name}')

        file = service.files().create(
            body=file_metadata,
            media_body=file_path
        ).execute()

        print('uploaded!')


# this entire class is specifically for google spreadsheet.
class gs_manager:
  endTimeStr = "endTime"
  endTypeStr = "endType"
  endStatStr = "endStatus"

  def log(input_time, input_type, output_stat):
    ''' stage one - main brain needs to upload pictures and upload token name to the spreadsheet
    outline
      1. find dateCell, tokenCell, and dataCell 
      2. if they match, input current session time and token into the cell
      3. push one cells below'''
    worksheet = bucket.worksheet

    # find date cell, token cell and data cell
    typeCell = worksheet.find(gs_manager.endTypeStr)
    timeCell = worksheet.find(gs_manager.endTimeStr)
    statCell = worksheet.find(gs_manager.endStatStr)

    # enter token cell
    if timeCell.col == 1 and typeCell.col == 2 and statCell.col ==3:
      print('datecell, tokenCell, dataCell is correctly oriented')
      worksheet.update_cell(timeCell.row, timeCell.col, f"{input_time}")
      worksheet.update_cell(typeCell.row, typeCell.col, f"{input_type}")
      worksheet.update_cell(statCell.row, statCell.col, f"{output_stat}")

    # enter new token and push cells to one cell bottom.
    worksheet.update_cell(timeCell.row + 1, timeCell.col, gs_manager.endTimeStr)
    worksheet.update_cell(typeCell.row +1, typeCell.col, gs_manager.endTypeStr)
    worksheet.update_cell(statCell.row + 1, statCell.col, gs_manager.endStatStr)

    