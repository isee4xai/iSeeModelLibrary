import sys
import pathlib
from flask import Flask, send_from_directory,request, json, jsonify
from flask_restful import Api
from flask_restful import Resource,reqparse
import matplotlib.pyplot
import random
import string
import tensorflow as tf
import numpy as np
import pandas as pd

from PIL import Image

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'Models'
ALLOWED_EXTENSIONS = {'h5'}
EXTENSION = '.h5'
NOT_ALLOWED_SYMBOLS = {'<', '>', ':', '\"', '/', '\\', '|', '\?', '*', '\''}

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
app = Flask(__name__)
api = Api(app)

app.secret_key = '^%huYtFd90;90jjj'
app.config['SESSION_TYPE'] = 'filesystem'

#We check the number of arguments passed to through the console

if len(sys.argv) > 2 :
    raise Exception("Too many arguments passed to the program")
else:
    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]):
            UPLOAD_FOLDER = sys.argv[1]
        else:
            raise Exception("The provided path does not exist")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@api.representation('image/png')
def output_file_png(data, code, headers):
    response = send_from_directory(UPLOAD_FOLDER,
    data["filename"],mimetype="image/png",as_attachment=True)
    return response

@api.representation('text/html')
def output_file_html(data, code, headers):
    response = send_from_directory(UPLOAD_FOLDER,
    data["filename"],mimetype="text/html",as_attachment=True)
    return response

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_id(userid):
    return not any(elem in NOT_ALLOWED_SYMBOLS for elem in userid)

@app.route('/upload_model', methods=['POST', 'PUT'])
def upload_model():
    #Add a new model to the server
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        parameters = request.form.get('params')
        if parameters is None:
            flash('No params part')
            return redirect(request.url)
        parameters = json.loads(parameters)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')   
            return redirect(request.url)
        if file and allowed_file(file.filename):
            userid = request.form.get('id')
            if userid is None or userid == '':
                filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
            else:
                if allowed_id(userid):
                    filename = userid
                else:
                    return 'The provided id is invalid'
            pathlib.Path(app.config['UPLOAD_FOLDER'], filename).mkdir(exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename, filename + EXTENSION))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename ,filename + '.json'), 'w') as f:
                json.dump(parameters, f)
            return jsonify(
                modelid = filename
            )
    #Update an existing model
    elif request.method == 'PUT':
        if 'file' not in request.files:
            flash('No file part')
            return 'A file hasnt been provided'

        iden = request.form.get('id')
        if iden is None:
            flash('No id provided')
            return "An id field is needed in order to update the model"

        parameters = request.form.get('params')
        if parameters is None:
            flash('No params part')
            return 'A param field is needed in order to update the model'
        file = request.files['file']
        parameters = json.loads(parameters)
        if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + EXTENSION))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden ,iden + '.json'), 'w') as f:
                json.dump(parameters, f)
            return "Model updated successfully"
        else:
            return "No model found with this id"

    return '''
    The only supported actions for this request are POST and PUT
    '''

@app.route('/dataset', methods=['POST', 'GET'])
def dataset():   
     if request.method == 'POST' :
        iden = request.form.get('id')
     elif request.method == 'GET':
        iden = request.args.get('id')
     else:
        return "The only supported actions for this request are POST and GET"      
     if iden is None:
        flash('No params part')
        return "The model id is missing"
     if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
         if request.method == 'POST' :
            if 'file' not in request.files:
                flash('No file part')
                return "A file is missing"
            file = request.files['file']
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '.pkl'))
            return "Dataset uploaded successfully"
         elif request.method == 'GET' :
            return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), iden + '.pkl', as_attachment=True)
         else:
            return "The only supported actions for this request are POST and GET"

     return "The model with the provided id doesn't exist"

@app.route('/delete', methods=['DELETE'])
def delete_model():
    iden = request.form.get('id')
    if iden is None:
        flash('No params part')
        return "The model id is missing"
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if request.method == 'DELETE':
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + EXTENSION))
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '.json'))
            if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '.pkl'))):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '.pkl'))
            os.rmdir(os.path.join(app.config['UPLOAD_FOLDER'], iden))
            return "Model deleted successfully"
        return "The only supported action for this request is DELETE"
    return "The model does not exist"

@app.route('/info', methods=['GET'])
def model_info():
    iden = request.args.get('id')
    if iden is None:
        flash('No params part')
        return "The model id is missing"
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if request.method == 'GET':
            return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), iden + '.json', as_attachment=True)
        return "The only supported action for this request is GET"
    return "The model does not exist"

@app.route('/Image/run', methods=['POST'])
def run_img_model():
    iden = request.form.get('id')
    if iden is None:
        flash('No params part')
        return "The model id is missing"
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if request.method == 'POST':
            model = tf.keras.models.load_model(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".h5"), compile=False)
            if 'image' not in request.files:
                flash('No file part')
                return "No image was provided"
            image = request.files['image']
            image = np.asarray(Image.open(image))
            try:
                predictions = model.predict(image[None,:,:])
                return jsonify({'predictions' : predictions.tolist()})
            except Exception as e:
                print(e)
                return "Something went wrong"
        return "The only supported action for this request is POST"
    return "The model does not exist"


@app.route('/Tabular/run', methods=['POST'])
def run_tab_model():
    iden = request.form.get('id')
    if iden is None:
        flash('No params part')
        return "The model id is missing"
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        instance = request.form.get('instance')
        if request.method == 'POST':
            model = tf.keras.models.load_model(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".h5"), compile=False)
            if instance is None:
                flash('No file part')
                return "No parameters were provided"
            instance = json.loads(instance)
            instance = instance['instance']
            X = tf.convert_to_tensor(instance)
            try:
                predictions = model.predict(X)
                return jsonify({'predictions' : predictions.tolist()})
            except Exception as e:
                print(e)
                return "Something went wrong"
        return "The only supported action for this request is POST"
    return "The model does not exist"

@app.route('/Text/run', methods=['POST'])
def run_text_model():
    iden = request.form.get('id')
    if iden is None:
        flash('No params part')
        return "The model id is missing"
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        instance = request.form.get('instance')
        if request.method == 'POST':
            model = tf.keras.models.load_model(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".h5"), compile=False)
            if instance is None:
                flash('No file part')
                return "No parameters were provided"
            instance = json.loads(instance)
            instance = instance['instance']
            X = tf.convert_to_tensor(instance)
            try:
                predictions = model.predict(X)
                return jsonify({'predictions' : predictions.tolist()})
            except Exception as e:
                print(e)
                return "Something went wrong"
        return "The only supported action for this request is POST"
    return "The model does not exist"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
