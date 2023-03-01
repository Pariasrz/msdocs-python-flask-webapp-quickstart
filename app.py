from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, make_response
from PIL import Image, ImageFilter
import io
app = Flask(__name__)


@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
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
   
   if name:
       print('Request for hello page received with name=%s' % name)
       # Create a response with the blurred image
       response = make_response(render_template('hello.html', name=name))
       response.headers.set('Content-Type', 'image/png')
       response.headers.set('Content-Disposition', 'inline', filename='blurred_image.png')
       response.set_data(img_bytes.getvalue())
       return response
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
