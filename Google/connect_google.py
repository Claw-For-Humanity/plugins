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
    ID_PARENT_DRIVE = None


    def __init__(DEFAULT_PATH, identity, spreadsheet_url, drive_url):
        ''' make sure to create ".creds" & ".imgs" folder on your base folder and put the cred json file into it.
        example is
        (default_base_folder, "cfh-hawkeye-xxxxxx", "xxxxxx (end of the spreadsheet addy)", "xxxxxx (end of the drive addy)")'''
        initializer.PATH_SERVICE_ACCOUNT_FILE = os.path.join(DEFAULT_PATH, '.creds', f'{identity}.json')
        initializer.PATH_CAPTURED_IMAGES = os.path.join(DEFAULT_PATH, '.imgs') 
        initializer.ID_PARENT_SPREADSHEET = spreadsheet_url
        initializer.ID_PARENT_DRIVE = drive_url

        # define creds and authenticate
        bucket.creds = initializer.authenticate()
        bucket.gc = gspread.authorize(bucket.creds)
        bucket.sh = bucket.gc.open('DetectedOutput') # TODO: open_by_key is an alternative for this
        bucket.worksheet = bucket.gc.open('DetectedOutput').sheet1


    def authenticate():
        creds = service_account.Credentials.from_service_account_file(initializer.PATH_SERVICE_ACCOUNT_FILE, scopes = initializer.SCOPES)
        return creds


class drive_manager:
    '''This class is specifically for uploading images on google drive.'''
    def upload_photo(image_name, upload_name = None):
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

        file_metadata = {
            'name':f"{upload_name}",
            'parents': [initializer.ID_PARENT_DRIVE]
        }

        file_path = os.path.join(initializer.PATH_CAPTURED_IMAGES, f'{image_name}')

        file = service.files().create(
            body=file_metadata,
            media_body=file_path
        ).execute()

        print('uploaded!')


# this entire class is specifically for google spreadsheet.
class gs_manager:
  endDateStr = "endDate"
  endTokenStr = "endToken"
  endDataStr = "endData"

  def mainInitiator(token):
    ''' stage one - main brain needs to upload pictures and upload token name to the spreadsheet
    outline
      1. find dateCell, tokenCell, and dataCell 
      2. if they match, input current session time and token into the cell
      3. push one cells below'''
    worksheet = bucket.worksheet
    cell_session_time = datetime.now().strftime("%Y%m%d%H%M%S")
    print(f"current cell time is {cell_session_time}")

    # find date cell, token cell and data cell
    dateCell = worksheet.find(gs_manager.endDateStr)
    tokenCell = worksheet.find(gs_manager.endTokenStr)
    dataCell = worksheet.find(gs_manager.endDataStr)

    # enter token cell
    if dateCell.col == 1 and tokenCell.col == 2 and dataCell.col ==3:
      print('datecell, tokenCell, dataCell is correctly oriented')
      worksheet.update_cell(dataCell.row, dataCell.col, f"uninferenced_{token}")
      worksheet.update_cell(tokenCell.row, tokenCell.col, f"{token}")
      worksheet.update_cell(dateCell.row, dateCell.col, f"{cell_session_time}")

    # enter new token and push cells to one cell bottom.
    worksheet.update_cell(dateCell.row + 1, dateCell.col, gs_manager.endDateStr)
    worksheet.update_cell(tokenCell.row +1, tokenCell.col, gs_manager.endTokenStr)
    worksheet.update_cell(dataCell.row + 1, dataCell.col, gs_manager.endDataStr)

    
  def colab_edit(infOut, token):
    '''for google colab
      stage two - google colab needs to inference pictures and upload data on spreadsheet
      outline
        1. match token from title 
        2. put inferenced data into the spreadsheet'''
    worksheet = bucket.worksheet
    uninferencedCell = worksheet.find(f"uninferenced_{token}")
    print(f"Found uninferenced data at R{uninferencedCell.row}C{uninferencedCell.col}")
    worksheet.update_cell(uninferencedCell.row, uninferencedCell.col, f"{infOut}")
    print('progress done')

  def accessor(token):
    '''stage three - main brain needs to have access to the inferenced data
    returns string output value '''
    outputValue = []
    worksheet = bucket.worksheet
    processedTokenCell = worksheet.find(f"{token}")
    

    if type(processedTokenCell) == type(None):
       print("couldn't find {}".format(token))
       return None
    
    else:
       time.sleep(5)
       dataCell = worksheet.find("endData")
       dRow = dataCell.row - processedTokenCell.row
       for i in range(dRow):
          cell = worksheet.cell(processedTokenCell.row+i, processedTokenCell.col + 1)
          outputValue.append({'cellData': cell.value})


    
    # processedDataCell = worksheet.cell(processedTokenCell.row, processedTokenCell.col + 1)
    # outputValue = processedDataCell.value
    
    print(f'row, col is r:{processedTokenCell.row} c:{processedTokenCell.col+1}')
    
    return outputValue