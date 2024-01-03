import sys
import requests
import os
import argparse
import _thread
import time
import subprocess
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

parser = argparse.ArgumentParser(description='Upload images')
parser.add_argument('--num_request', type=int, help='one image per request')
parser.add_argument('--url', type=str, help='URL to the backend server, e.g. http://3.86.108.221/xxxx.php')
parser.add_argument('--image_folder', type=str, help='the path of the folder where images are saved on your local machine')

args = parser.parse_args()
url = args.url


def send_one_request(image_path):
    # Define http payload, "myfile" is the key of the http payload
    file = {"myfile": open(image_path,'rb')} 
    print('file sent : ',image_path)
    r = requests.post(url, files=file)
    print('status',r.status_code)
    # print('return value ',r)
    # Print error message if failed

    if r.status_code != 200:
        # print('enter if')
        print('sendErr: '+r.url)
    else :       
        # print('enter else',image_path)
        image_msg = image_path.split('\\')[-1] + ' uploaded!'
        # print('image_msg:',image_msg)
        msg = image_msg + '\n' + 'Classification result: ' + r.text
        print(msg)

start_time = time.time()

num_request = args.num_request
image_folder = args.image_folder
num_max_workers = 100
image_path_list = []
for i, name in enumerate(os.listdir(image_folder)):
    if i == num_request:
        break
    image_path_list.append(image_folder + name)


with ThreadPoolExecutor(max_workers = num_max_workers) as executor:
      executor.map(send_one_request, image_path_list)
