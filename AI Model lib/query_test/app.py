import sys
import pathlib
from flask import Flask, send_from_directory,request, json, jsonify
from flask_restful import Api
from flask_restful import Resource,reqparse
import matplotlib.pyplot
import random
import string
import numpy as np
import pandas as pd
import joblib
from skimage.io import imread
from skimage.transform import resize
from sklearn.base import is_classifier, is_regressor
from pathlib import Path
import sklearn
from flask_cors import CORS, cross_origin


from PIL import Image

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'Models'
ALLOWED_EXTENSIONS = {'pkl'}
EXTENSION = '.pkl'
NOT_ALLOWED_SYMBOLS = {'<', '>', ':', '\"', '/', '\\', '|', '\?', '*'}


cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
app = Flask(__name__)
api = Api(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Ty'

app.secret_key = '^%huYtFd90;90jjj'
app.config['SESSION_TYPE'] = 'filesystem'

#We check the number of arguments passed to through the console

if len(sys.argv) > 2 :
    raise Exception("Too many arguments passed to the program")
else:
    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]):
            if os.path.isdir(sys.argv[1]):
                print("Using existing directory '" +sys.argv[1]+ "'")
            else:
                raise Exception("A non-directory file named '" + sys.argv[1]+ "' already exists. Please use another name.")
        else:
            os.mkdir(sys.argv[1])
            print("The '" +sys.argv[1]+ "' directory was created.")
            UPLOAD_FOLDER = sys.argv[1]

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
                json.dump(parameters, f, ensure_ascii = False)
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
            model = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + EXTENSION))
            if 'image' not in request.files:
                flash('No file part')
                return "No image was provided"
            image = request.files['image']
            image = np.asarray(Image.open(image))
            try:
                #if it's a classification model we try to launch predict_proba
                if is_classifier(model):
                    try: 
                        predictions = model.predict_proba(image[None,:,:])
                        return jsonify({'predictions' : predictions.tolist()})
                    except Exception as e:
                        predictions = model.predict(image[None,:,:])
                        return jsonify({'predictions' : predictions.tolist()})
                else:
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
        data = request.form.get('data')
        if request.method == 'POST':
            model = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + EXTENSION))
            if data is None:
                flash('No file part')
                return "No parameters were provided"
            data = json.loads(data)
            data = data['instance']
            data = np.asarray(data)
            X = pd.DataFrame(data).T
            try:
                 #if it's a classification model we try to launch predict_proba
                if is_classifier(model):
                    try:
                        predictions = model.predict_proba(X)
                        return jsonify({'predictions' : predictions.tolist()})
                    except Exception as e:
                        predictions = model.predict(X)
                        return jsonify({'predictions' : predictions.tolist()})
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
        data = request.form.get('data')
        if request.method == 'POST':
            model = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + EXTENSION))
            if data is None:
                flash('No file part')
                return "No parameters were provided"
            data = json.loads(data)
            data = data['instance']
            X = tf.convert_to_tensor(instance)
            try:
                predictions = model.predict(X)
                return jsonify({'predictions' : predictions.tolist()})
            except Exception as e:
                print(e)
                return "Something went wrong"
        return "The only supported action for this request is POST"
    return "The model does not exist"

@app.route('/query', methods=['POST', 'GET', 'DELETE'])
def query_control():   
     if request.method == 'POST' :
        iden = request.form.get('id')
        if iden is None:
            flash('No params part')
            return "The model id is missing"
        if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
            if 'query' not in request.form and 'image' not in request.files:
                flash('No query or image')
                return "The query and image field are missing"
            filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
            if 'image' in request.files:
                image = request.files['image']
                extension = (image.filename).rsplit('.', 1)[1].lower()
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], iden, filename + '.' + extension))
                return "Image saved with id: " + filename
            else:    
                query = request.form.get('query')
                auxjson = {"query" : query}
                with open(os.path.join(app.config['UPLOAD_FOLDER'], iden ,filename + '.json'), 'w') as f:
                    json.dump(auxjson, f)
                return "Query saved with id: " + filename
     elif request.method == 'GET':
        iden = request.args.get('id')
        query_id = request.args.get('query_id')
        if iden is None:
            flash('No params part')
            return "The model id is missing"
        if query_id is None:
            flash('No params part')
            return "The query id is missing"
        if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
            for root, dirs, files in os.walk(os.path.join(app.config['UPLOAD_FOLDER'], iden)):
                for name in files:
                    if query_id in name:
                        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), name, as_attachment=True)
            return "No query exists for with the provided id"

     elif request.method == 'DELETE':
        iden = request.args.get('id')
        query_id = request.args.get('query_id')
        if iden is None:
            flash('No params part')
            return "The model id is missing"
        if query_id is None:
            flash('No params part')
            return "The query id is missing"
        if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
           for root, dirs, files in os.walk(os.path.join(app.config['UPLOAD_FOLDER'], iden)):
                for name in files:
                    if query_id in name:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden, name))
                        return "Query removed successfully"
           return "No query exists with the provided id"
     else:
        return "The only supported actions for this request are POST, GET and DELETE"
     return "The model with the provided id doesn't exist"

@app.route('/model_list', methods=['GET'])
def model_list():
    model_list = {}
    for iden in os.listdir(app.config['UPLOAD_FOLDER']):
        f = open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '.json'))
        params = json.load(f)
        model_list.update({iden : params['alias']})
    return jsonify(model_list)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
