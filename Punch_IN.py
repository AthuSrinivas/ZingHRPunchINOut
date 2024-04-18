import random
import string
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import requests
import win32ui
import win32con
import json

Emp_id = ''
PlainTextPassword = ''
# Add APIToken (Mandatory) 
APIToken = ''

def strip_of_spaces(line_string):
    return line_string.strip()

def get_credentials_from_file(fileh="zing_credentials.txt"):
    global Emp_id, PlainTextPassword
    with open(fileh, 'r') as f:
        line_data = f.readlines()
        empID_line = strip_of_spaces(line_data[0])
        Emp_id = empID_line.split("EmployeeID:")[1]
        pass_line = strip_of_spaces(line_data[1])
        PlainTextPassword = pass_line.split("Password:")[1]

def encrypt_aes(plain_password, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(plain_password.encode('utf-8'), AES.block_size)
    encrypted_password = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_password).decode('utf-8')

def generate_random_key(length=16):
  chars = string.digits
  random_key = ''.join(random.choice(chars) for i in range(length))
  return random_key

# Get current date with UTC timezone
current_date = datetime.utcnow()

# Format date components with leading zeros if necessary
day = current_date.strftime("%d")
day = "0" + day if len(day) == 1 else day
month = current_date.strftime("%m")
month = "0" + month if len(month) == 1 else month
year = current_date.strftime("%Y")

# Construct the IVKey string
IVKey = f"{day}/{month}/{year}ZingHR"

# Generate a random key with default length (16 characters)
random_key = generate_random_key()

#encrypt Password
try:
    get_creds = get_credentials_from_file()
except:
    response_ui = win32ui.MessageBox("Please check if zing_credential.txt file is in the same folder as the EXE!", "Punch In", win32con.MB_OK)
    exit()
key = random_key.encode('utf-8')
iv = IVKey.encode('utf-8')
encrypted_password = encrypt_aes(PlainTextPassword, key, iv)


# URL of the page you want to request
url = "https://portal.zinghr.com/2015/route/Auth/PunchInOut"

# Custom headers
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US",
    "Authorization": "apikey:APIKEY,tokenid:"+APIToken,
    "Connection": "keep-alive",
    "Content-Length": "143",
    "Content-Type": "application/json; charset=UTF-8",
    "Cookie": "",
    "Host": "portal.zinghr.com",
    "Origin": "https://portal.zinghr.com",
    "Referer": "https://portal.zinghr.com/2015/pages/authentication/zing.aspx?ccode=embitel",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}

# Data to be sent in the request body (if any)
data = {"Subscription":"embitel","Type":"PUNCHIN","UserId":Emp_id,"Empcode":Emp_id,"Password":encrypted_password,"SyncVal":random_key}
try:
# Send POST request with custom headers and data (if any)
    response = requests.post(url, headers=headers, json=data)
    # Check if request was successful (status code 200)
    if response.status_code == 200:
        text_dict = json.loads(response.text)
        Table1 = eval(text_dict['Table1'])[0]
        response_ui = win32ui.MessageBox(Table1['MSG'], "Punch In", win32con.MB_OK)
    else:
        response_ui = win32ui.MessageBox("Punch-In Failed!\nPlease Check for the following:\n  1.Credentials are Properly given in zing_credentials.txt file.\n  2.If you are connected properly to internet.", "Punch In", win32con.MB_OK)
except:
    response_ui = win32ui.MessageBox("Please check if you are connected to the Internet!", "Punch In", win32con.MB_OK)
    
