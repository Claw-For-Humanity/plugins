import gspread
from datetime import datetime
from google.oauth2 import service_account
import os

class bucket:
   creds = None
   gc = None
   sh = None
   worksheet = None


class initializer:
    SCOPES = ['https://www.googleapis.com/auth/drive'] # final

    PATH_SERVICE_ACCOUNT_FILE = None
    PATH_CAPTURED_IMAGES = None
    ID_PARENT_FOLDER = None


    def __init__(DEFAULT_PATH, account_id, destination_parent_id):
        '''example is
        (default_base_folder, "cfh-hawkeye-xxxxxx", "xxxxxx (end of the addy)")'''
        initializer.PATH_SERVICE_ACCOUNT_FILE = os.path.join(DEFAULT_PATH, 'data', f'{account_id}.json')
        initializer.PATH_CAPTURED_IMAGES = os.path.join(DEFAULT_PATH, 'capturedImages')
        initializer.ID_PARENT_FOLDER = destination_parent_id

        # define creds and authenticate
        bucket.creds = initializer.authenticate()
        bucket.gc = gspread.authorize(bucket.creds)
        bucket.sh = bucket.gc.open('DetectedOutput')
        bucket.worksheet = bucket.gc.open('DetectedOutput').sheet1


    def authenticate():
        creds = service_account.Credentials.from_service_account_file(initializer.PATH_SERVICE_ACCOUNT_FILE, scopes = initializer.SCOPES)
        return creds


class tools:
  def current_time():
    now = datetime.now()
    year_month_time = now.strftime("%Y%m%d%H%M%S")
    return year_month_time

class editor:
  endDateStr = "endDate"
  endTokenStr = "endToken"
  endDataStr = "endData"

  def edit():
    worksheet = bucket.worksheet
    cell_session_time = tools.current_time()

    # Find a cell with exact string value
    dateCell = worksheet.find(editor.endDateStr)
    print(dateCell)
    tokenCell = worksheet.find(editor.endTokenStr)
    print(tokenCell)
    dataCell = worksheet.find(editor.endDataStr)
    print(dataCell)
    print("Found something at R%sC%s" % (dateCell.row, dateCell.col))
    if dateCell.col == 1 and tokenCell.col == 2 and dataCell.col ==3:
      print('datecell, tokenCell, dataCell is correctly oriented')
      # it's going to replace the old value to whatever date and time it is
      worksheet.update_cell(dateCell.row, dateCell.col,cell_session_time)
      worksheet.update_cell(tokenCell.row, tokenCell.col, "token received from the title of the picture")
      worksheet.update_cell(dataCell.row, dataCell.col, "data -- inference output")

    else:
      print('safety protocol.. something is off')
      exit()

    print('changing values')
    worksheet.update_cell(dateCell.row + 1, dateCell.col, editor.endDateStr)
    worksheet.update_cell(tokenCell.row +1, tokenCell.col, editor.endTokenStr)
    worksheet.update_cell(dataCell.row + 1, dataCell.col, editor.endDataStr)
    print('changing values done')
i = 0
initializer.__init__('D:\GitHub\CFH\plugins', 'cfh-hawkeye-82742a86d820', '1OlbAmA_yr76eaoT217e3nyAdT9X7ZkBh')
editor.edit()