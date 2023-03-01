from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
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
   file = request.files['image']
   # check if the file has an allowed image file extension
   img = Image.open(io.BytesIO(file.read()))
   # apply a blur filter to the image
   blurred_img = img.filter(ImageFilter.BLUR)
   # convert the blurred image to a byte stream for display in the HTML page
   img_io = io.BytesIO()
   blurred_img.save(img_io, 'JPEG', quality=70)
   img_io.seek(0)
   
   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name, img_data=img_io.getvalue())
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()
