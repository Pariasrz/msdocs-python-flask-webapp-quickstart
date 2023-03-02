# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 20:28:03 2023

@author: Pariya
"""

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response
from PIL import Image, ImageFilter
import io
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content


app = Flask(__name__)

app.config['SENDGRID_API_KEY'] = '<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>'


# Blob Storage Configuration
CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=coviddiag;AccountKey=7KQqN6FW0gMWg9rL8XPk6v0t6OgrPtq3ijeqou2k6OAU9fabGOHIBHKoZV3dkkR4Fr3QpwPgzYDk+AStyCfFkA==;EndpointSuffix=core.windows.net'
CONTAINER_NAME = 'imageprocess'
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

'''
@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')
'''
@app.route('/', methods=['GET', 'POST'])
def index():
   if request.method == 'POST':
      email = request.form.get('email')
      password = request.form.get('password')
      
      # Retrieve the password for the entered email from Azure Blob Storage
      blob_name = f"{email}.txt"
      blob_client = container_client.get_blob_client(blob_name)
      blob_data = blob_client.download_blob().content_as_text()

      if blob_data == password:
         return render_template('hello.html')
      else:
         # Passwords don't match, redirect to index page
         print('Incorrect email or password -- redirecting')
         return redirect(url_for('index'))
   
   # Render the index page with the login form
   return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/hello', methods=['GET', 'POST'])
def hello():
   if request.method == 'POST':
      # Get the uploaded file
      image = request.files['image']
      # Open the image file and apply blur filter
      img = Image.open(image)
      blurred_img = img.filter(ImageFilter.BLUR)
      # Convert the blurred image to bytes and store in memory
      img_bytes = io.BytesIO()
      blurred_img.save(img_bytes, format='PNG')
      img_bytes.seek(0)
      if image:
         #print('Request for hello page received with name=%s' % request.form.get('name'))
         # Create a response with the blurred image
         response = make_response(render_template('blur.html'))
         response.headers.set('Content-Type', 'image/png')
         response.headers.set('Content-Disposition', 'inline', filename='blurred_image.png')
         response.set_data(img_bytes.getvalue())
         return response
      else:
         print('Request for hello page received with no name or blank name -- redirecting')
         return redirect(url_for('hello'))

   # Render the hello page with the image upload form
   return render_template('hello.html')


'''
2
@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')
   
   # Get the username and password from the form
   email = request.form.get('email')
   password = request.form.get('password')

   if email and password:
      print('Request for hello page received with name=%s and email=%s, password=%s' % (name, email, password))
        
      # Retrieve the password for the entered email from Azure Blob Storage
      blob_name = f"{email}.txt"
      blob_client = container_client.get_blob_client(blob_name)
      blob_data = blob_client.download_blob().content_as_text()
      
      if blob_data == password:
         return redirect(url_for('hello'))
      else:
         # Passwords don't match, redirect to index page
         print('Incorrect email or password -- redirecting')
         return redirect(url_for('index'))
   else:
      print('Request for hello page received with no name or blank name -- redirecting')
      return redirect(url_for('index'))
'''
'''
1
def hello():
   name = request.form.get('name')
   img_file = request.files['image']
   # Open the image file and apply blur filter
   img = Image.open(img_file)
   blurred_img = img.filter(ImageFilter.BLUR)
   # Convert the blurred image to bytes and store in memory
   img_bytes = io.BytesIO()
   blurred_img.save(img_bytes, format='PNG')
   img_bytes.seek(0)
   
   # Get the username and password from the form
   email = request.form.get('email')
   password = request.form.get('password')

   if email and password:
      print('Request for hello page received with name=%s and email=%s, password=%s' % (name, email, password))
        
      # Retrieve the password for the entered email from Azure Blob Storage
      blob_name = f"{email}.txt"
      blob_client = container_client.get_blob_client(blob_name)
      blob_data = blob_client.download_blob().content_as_text()
      
      if blob_data == password:
         # Passwords match, return the blurred image
         response = make_response(render_template('hello.html', name=name))
         response.headers.set('Content-Type', 'image/png')
         response.headers.set('Content-Disposition', 'inline', filename='blurred_image.png')
         response.set_data(img_bytes.getvalue())
         return response
      else:
         # Passwords don't match, redirect to index page
         print('Incorrect email or password -- redirecting')
         return redirect(url_for('index'))
   else:
      print('Request for hello page received with no name or blank name -- redirecting')
      return redirect(url_for('index'))
'''

@app.route('/signup', methods=['POST','GET'])
def signup():
   if request.method == 'POST':
      # Get the user's information from the form
      name = request.form.get('name')
      email = request.form.get('email')
      password = request.form.get('password')

      # Check if the email already exists
      blob_name = f"{email}.txt"
      blob_client = container_client.get_blob_client(blob_name)
      if blob_client.exists():
         return render_template('signup.html', error="Email already exists.")
        
      # Create a new blob with the user's password
      container_client.upload_blob(name=blob_name, data=password)
      
      # Create a new Mail object
      message = Mail(
      from_email='paria.sarzaeim@ontariotechu.net',
      to_emails=email,
      subject='Welcome to My Web App!',
      html_content='Thank you for signing up!')
      
      # Use the sendgrid client to send the email
      try:
         sg = sendgrid.SendGridAPIClient(app.config['SENDGRID_API_KEY'])
         response = sg.send(message)
         print(f'Successfully sent email to {email}')
      except Exception as e:
         print(f'Error sending email to {email}: {str(e)}')


      # Redirect to the index page
      return redirect(url_for('index'))

   # If the request method is GET, render the signup page
   return render_template('sign-up.html')

'''
@app.route('/login', methods=['POST'])
def login():
   name = request.form.get('name')
   img_file = request.files['image']
   # Open the image file and apply blur filter
   img = Image.open(img_file)
   blurred_img = img.filter(ImageFilter.BLUR)
   # Convert the blurred image to bytes and store in memory
   img_bytes = io.BytesIO()
   blurred_img.save(img_bytes, format='PNG')
   img_bytes.seek(0)
   
   # Get the username and password from the form
   email = request.form.get('email')
   password = request.form.get('password')

   if email and password:
      print('Request for hello page received with name=%s and email=%s, password=%s' % (name, email, password))
        
      # Store the username and password in Azure Blob Storage
      blob_name = f"{email}.txt"
      blob_client = container_client.get_blob_client(blob_name)
      blob_client.upload_blob(password.encode())

      #return render_template('hello.html', name=name, blurred_img=img_bytes.getvalue())
      
      
      # Create a response with the blurred image
      response = make_response(render_template('hello.html', name=name))
      response.headers.set('Content-Type', 'image/png')
      response.headers.set('Content-Disposition', 'inline', filename='blurred_image.png')
      response.set_data(img_bytes.getvalue())
      return response
   else:
      print('Request for hello page received with no name or blank name -- redirecting')
      return redirect(url_for('index'))  
'''

if __name__ == '__main__':
   app.run()
