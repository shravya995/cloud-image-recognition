from flask import Flask, render_template, request, redirect, url_for, session
import boto3, botocore
import os
import uuid
import time
import random
from sqs_request_queue import sendMessage,receive_and_delete_messages




app = Flask(__name__)

aws_session = boto3.Session(profile_name="default")

app.config['S3_BUCKET'] = "cloud-project1-input-images"
app.config['S3_LOCATION'] = 'http://{}.s3.amazonaws.com/'.format('cloud-project1-input-images')


app.config['UPLOAD_FOLDER'] = 'C:/Users/Shravya/Desktop/sample'
app.secret_key = '123!@#123'



s3 = aws_session.resource(
   "s3"
)

sqs_client =aws_session.client("sqs")

def generate_id():
    return str(uuid.uuid4())+'.png'

@app.route('/')
def index():
   return render_template('index.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
        file = request.files['myfile']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        file_name=file.filename
        s3 = aws_session.client('s3')
        bucket = app.config['S3_BUCKET']
      #   key_name=generate_id()
        key_name=file.filename
        session['id'] = key_name 
        message=key_name+'#'+file_name
        s3.upload_file(os.path.join(app.config['UPLOAD_FOLDER'], file.filename), bucket, file_name)
        sendMessage(message,sqs_client)
        # time.sleep(random.randint(0,30))
        max_queue_messages=10
        while True:
         print('Key Value',key_name)
         result=receive_and_delete_messages('Shrav-Response-Queue.fifo',max_queue_messages,sqs_client,key_name)
         if result !=None:
            print('Value returned',result)
            return result
            break
         print('None returned')

        return 'No Result!'

@app.route('/result', methods = ['GET'])		
def get_image():
    user_id=session['id']
    return user_id




if __name__=='__main__':
   
   app.run(debug=True,threaded = True)
    