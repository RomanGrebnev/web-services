from flask import Flask, request, jsonify, abort, \
    redirect, url_for, render_template
app = Flask(__name__)
import numpy as np
from joblib import load

knn = load('knn.pkl')

@app.route('/')
def hello_world():
    print('hi 1+1')
    return '<h1>Hello, my best very friend!!!!!!!</h1>'

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    username = float(username) * float(username)
    return 'User %s' % username

@app.route('/avg/<nums>')
def avg(nums):
    # show the user profile for that user
    nums = nums.split(',')
    print(nums)
    return str(nums)

@app.route('/iris/<param>')
def iris(param):
    
    param = param.split(',')
    param = [float(num) for num in param]
    print(param)
    param = np.array(param).reshape(1,-1)
    predict = knn.predict(param)
    return str(predict)

@app.route('/show_image')
def show_image():
    return '<img src="/static/setosa.jpg" alt = "setosa">'

@app.route('/badrequest400')
def bad_request():
    return abort(400)

@app.route('/iris_post', methods=['POST'])
def add_message():
    content = request.get_json()

    try:
        param = content['flower'].split(',')
        param = [float(num) for num in param]
        print(param)
        param = np.array(param).reshape(1,-1)
        predict = knn.predict(param)
        predict = {'class':str(predict[0])}
    except:
        return redirect(url_for('bad_request'))

    return jsonify(predict)


from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
import pandas as pd
from flask import send_file

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    file = FileField()

@app.route('/submit', methods=('GET', 'POST'))
def submit():
    form = MyForm()
    if form.validate_on_submit():
        print(form.name.data)

        f = form.file.data
        filename = form.name.data + '.txt'
        # # filename = secure_filename(f.filename)
        # f.save(os.path.join(filename))
        df = pd.read_csv(f, header = None)
        predict = knn.predict(df)
        print(predict)
        print(df.head)

        result = pd.DataFrame(predict)
        result.to_csv(filename, index = False)

        return send_file(filename,
                     mimetype='text/csv',
                     attachment_filename=filename,
                     as_attachment=True)
    return render_template('submit.html', form=form)


import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename + 'uploaded')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'file uploaded'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
