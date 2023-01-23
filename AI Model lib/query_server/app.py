import sys
import pathlib
from flask import Flask, send_from_directory,request, json, jsonify
from flask_restful import Api
import random
import string
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from flask_cors import CORS, cross_origin
import os
import shutil
import zipfile
import csv
from flask import Flask, flash, request
import requests
from urllib3.exceptions import InsecureRequestWarning
from PIL import Image

UPLOAD_FOLDER = 'Models'
ALLOWED_EXTENSIONS = {'pkl', 'h5','pt'}
NOT_ALLOWED_SYMBOLS = {'<', '>', ':', '\"', '/', '\\', '|', '\?', '*'}


cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
app = Flask(__name__)
api = Api(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Ty'
app.secret_key = '^%huYtFd90;90jjj'
app.config['SESSION_TYPE'] = 'filesystem'

#URLS={"sklearn":"https://models-sk-dev.isee4xai.com/",
#      "xgboost":"https://models-sk-dev.isee4xai.com/",
#      "TF1":"https://models-tf-dev.isee4xai.com/",
#      "TF2":"https://models-tf-dev.isee4xai.com/",
#      "TF":"https://models-tf-dev.isee4xai.com/"}

URLS={  "sklearn":"http://models-sk:5000",
	"xgboost":"http://models-sk:5000",
	"TF1":"http://models-tf:5000",
	"TF2":"http://models-tf:5000",
	"TF":"http://models-tf:5000"}

#URLS={  "sklearn":"http://localhost:5000",
#	"xgboost":"http://localhost:5000",
#	"TF1":"http://localhost:5000",
#	"TF2":"http://localhost:5000",
#	"TF":"http://localhost:5000"}



DATASET_TYPES=["Tabular", "Text", "Image"]

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
#We check the number of arguments passed to through the console

if len(sys.argv) > 2 :
    raise Exception("Too many arguments passed to the program")
else:
    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]):
            if os.path.isdir(sys.argv[1]):
                print("Using existing directory '" +sys.argv[1]+ "'")
                UPLOAD_FOLDER = sys.argv[1]
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

def allowed_id(iden):
    for c in NOT_ALLOWED_SYMBOLS:
        if c in iden:
            return False
    return True

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/num_instances/<string:iden>',methods=['GET'])
def num_instances(iden):
    if iden is None:
        flash('No id part')
        return "The model id is missing."
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json"))):
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json"), 'r') as file:
                model_info=json.load(file)
        else:
             return "There is no configuration file for this model."

        #For Images
        if(model_info["dataset_type"].lower()=="image"):
            #from image folder
            folder_path=os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data")
            if(os.path.exists(folder_path)):
                return str(len(os.listdir(folder_path)))
            elif(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv"))): 
                with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv")) as f:
                    return str(sum(1 for line in f))
            else:
                return "No training data was uploaded for this model."
        #for rest
        if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.pkl"))):
            df = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.pkl"))
            try:
                return str(len(df.shape[0]))
            except:
                return "Could not extract number of instances from the data."
        else:
            return "No training data was uploaded for this model."
    else:
        return "The model does not exist."

@app.route('/instance/<string:iden>/<int:index>',methods=['GET'])
def instance(iden, index):
    if iden is None:
        flash('No id part')
        return "The model id is missing."
    if index is None:
        flash('No index part')
        return "The index is missing."
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json"))):
                with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json"), 'r') as file:
                    model_info=json.load(file)
        else:
             return "There is no configuration file for this model."

        #For Images
        if(model_info["dataset_type"].lower()=="image"):

            #from image folder
            folder_path=os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data")
            if(os.path.exists(folder_path)):  
                if(index>=0 and index<len(os.listdir(folder_path))):
                    try:
                        #sending
                        return send_from_directory(folder_path, os.listdir(folder_path)[index], as_attachment=True)
                    except Exception as e:
                        print(e)
                        return "Could not send image file."
                else:
                    return "The index is invalid. The index must be between 0 and " + str(len(os.listdir("HANDWRITTN_data")-1))

            #from csv
            elif(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv"))): 
                instance=None
                df=pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv"),header=None)
                instance=df.iloc[[index]].to_numpy()[0]
                #reshaping
                try:
                    instance=instance.reshape(tuple(model_info["attributes"]["features"]["image"]["shape_raw"]))
                    print(instance)
                except Exception as e:
                    print(e)
                    return "Could not reshape instance."
                #denormalizing
                nmin=model_info["attributes"]["features"]["image"]["min"]
                nmax=model_info["attributes"]["features"]["image"]["max"]
                min_raw=model_info["attributes"]["features"]["image"]["min_raw"]
                max_raw=model_info["attributes"]["features"]["image"]["max_raw"]
                try:
                    instance=(((instance-nmin)/(nmax-nmin))*(max_raw-min_raw)+min_raw).astype(np.uint8)
                except:
                    return "Could not denormalize instance."
                #converting to image
                im=None
                try:
                    im=Image.fromarray(instance)
                except Exception as e:
                    print(e)
                    return "Could not convert instance to PNG file."
                #sending
                try:
                    im.save(os.path.join(app.config['UPLOAD_FOLDER'], iden,iden + "_instance.png"))   
                    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), iden + "_instance.png", as_attachment=True)
                except Exception as e:
                    print(e)
                    return "Could not send PNG file."
            else:
                return "No training data was uploaded for this model."
        
        #For the rest
        if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.pkl"))):
            df = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.pkl"))
            try:
                target_names=model_info["attributes"]["target_names"]
            except:
                return "Could not extract target columns from model information. Please update the model attributes file."
            try:
                df.drop(target_names, axis=1,inplace=True)
            except:
                return "Could not drop target feature/s"
            try:
                instance=df.iloc[[index]].values.tolist()
                return str(instance)

            except Exception as e:
                print(e)
                return "Could not get the instance from the data."
        else:
            return "There is no training file for this model."
    else:
        return "The model does not exist"



@app.route('/instanceJSON/<string:iden>/<int:index>',methods=['GET'])
def instanceJSON(iden, index):
    if iden is None:
        flash('No id part')
        return "The model id is missing."
    if index is None:
        flash('No index part')
        return "The index is missing."
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.pkl"))):
            df = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.pkl"))
            if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json"))):
                with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json"), 'r') as file:
                    model_info=json.load(file)
            else:
                return "The model information file does not exist."
            try:
                target_names=model_info["attributes"]["target_names"]
            except:
                return "Could not extract target columns from model information. Please update the model attributes file."
            try:
                df.drop(target_names, axis=1,inplace=True)
            except:
                return "Could not drop target feature/s"
            try:
                instance=df.iloc[[index]]
            except:
                return "Could not get the instance from the data."
            try:
                return json.loads(instance.to_json(orient="table",index=False))["data"][0]
            except Exception as e:
                print(e)
                return "Could not convert the instance to JSON. Make sure the provided model information contains the target names in the expected format and matches the given dataset."
        else:
            return "There is no training file for this model."
    else:
        return "The model does not exist"

@app.route('/upload_model', methods=['POST', 'PUT'])
def upload_model():
    #Add a new model to the server
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return 'No file part'
        parameters = request.form.get('info')
        if parameters is None:
            flash('No info part')
            return 'No info part'
        parameters = json.loads(parameters)
        if "alias" not in parameters:
            flash('No alias part')
            return("The alias of the model was not specified.")
        if "backend" not in parameters:
            flash('The model backend was not specified.')
            return("The backend was not specified.")
        if "model_task" not in parameters:
            flash('The model task was not specified.')
            return 'The model task was not specified.'
        if "dataset_type" not in parameters:
            flash('The dataset type was not specified.')
            return 'The dataset type was not specified.'
        if "attributes" not in parameters:
            flash('The attributes for this model were not specified.')
            return 'The attributes for this model were not specified.'
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')   
            return "No selected file"
        if file and allowed_file(file.filename):
            userid = request.form.get('id')
            if userid is None or userid == '':
                filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
            else:
                if allowed_id(userid):
                    filename = userid
                    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], userid)):
                        return 'A model with the id: ' + userid + ' already exists'
                else:
                    return 'The provided id is invalid'
            pathlib.Path(app.config['UPLOAD_FOLDER'], filename).mkdir(exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename, filename + "."+file.filename.rsplit('.', 1)[1].lower()))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename ,filename + '.json'), 'w') as f:
                json.dump(parameters, f, ensure_ascii = False)
            return jsonify(
                modelid = filename
            )
        else:
            return "The type of file passed is not supported"
    #Update an existing model
    elif request.method == 'PUT':
        if 'file' not in request.files:
            flash('No file part')
            return 'A file has not been provided'

        iden = request.form.get('id')
        if iden is None:
            flash('No id provided')
            return "An id field is needed in order to update the model"

        parameters = request.form.get('info')
        if parameters is None:
            flash('No info part')
            return 'A info field is needed in order to update the model'
        file = request.files['file']
        parameters = json.loads(parameters)
        if "alias" not in parameters:
            flash('No alias part')
            return("The alias of the model was not specified.")
        if "backend" not in parameters:
            flash('The model backend was not specified.')
            return("The backend was not specified.")
        if "model_task" not in parameters:
            flash('The model task was not specified.')
            return 'The model task was not specified.'
        if "dataset_type" not in parameters:
            flash('The dataset type was not specified.')
            return 'The dataset type was not specified.'
        if "attributes" not in parameters:
            flash('The attributes for this model were not specified.')
            return 'The attributes for this model were not specified.'
        
        if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "."+file.filename.rsplit('.', 1)[1].lower()))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden ,iden + '.json'), 'w') as f:
                json.dump(parameters, f,ensure_ascii = False)
            return "Model updated successfully"
        else:
            return "No model found with this id"

    return "The only supported actions for this request are POST and PUT"

@app.route('/dataset', methods=['POST', 'GET'])
def dataset():   
     if request.method == 'POST' :
        iden = request.form.get('id')
     elif request.method == 'GET':
        iden = request.args.get('id')
     else:
        return "The only supported actions for this request are POST and GET" 
     if iden is None:
        flash('No id part')
        return "The model id is missing"
     if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
         if request.method == 'POST' :
            if 'file' not in request.files:
                flash('No file part')
                return "A file is missing"
            file = request.files['file']
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
                model_info=json.load(f)
            #For Images
            if(model_info["dataset_type"].lower()=="image"):
                #zip file with images
                if(file.content_type=="application/zip"):
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".zip"))
                    folder_path_temp=os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_datatemp")
                    os.mkdir(folder_path_temp)
                    with zipfile.ZipFile(file) as zip_ref:
                        for zip_info in zip_ref.infolist():
                            if zip_info.filename[-1] in ['/','\\']:
                                continue
                            zip_info.filename = os.path.basename(zip_info.filename)
                            zip_ref.extract(zip_info, folder_path_temp)
                    folder_path=os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data")
                    if os.path.exists(folder_path):
                        shutil.rmtree(folder_path)
                    os.rename(folder_path_temp,folder_path)
                    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden,iden + '_data.csv')):
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden,iden + '_data.csv')) 
                #csv with flattened images  
                elif(file.content_type=="text/csv"):
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], iden,iden + '_data.csv'))  
                    folder_path=os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data")
                    if os.path.exists(folder_path):
                        shutil.rmtree(folder_path)
                    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".zip")):
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".zip"))
                else:                               
                    return "The training data must be a .zip or .csv file."
                if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden,iden + '_instance.png')):
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden,iden + '_instance.png'))  
                return "Dataset uploaded successfully."
            #rest
            elif(1):
                try:
                    df=pd.read_csv(file,header=None)
                except:
                    return "Could not convert .csv file to Pandas Dataframe."
                joblib.dump(df,os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '_data.pkl'))           
            return "Dataset uploaded successfully"
         elif request.method == 'GET' :
            if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '_data.csv'))):
                return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), iden + '_data.csv', as_attachment=True)
            elif (os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden+".zip"))):
                return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), iden + '.zip', as_attachment=True)
            else:
                return "No training file has been uploaded."
         else:
            return "The only supported actions for this request are POST and GET"
     return "The model with the provided id doesn't exist"

@app.route('/dataset_cockpit', methods=['POST', 'GET'])
def dataset_cockpit():   
     if request.method == 'POST' :
        iden = request.form.get('id')
     elif request.method == 'GET':
        iden = request.args.get('id')
     else:
        return "The only supported actions for this request are POST and GET" 
     if iden is None:
        flash('No id part')
        return "The model id is missing"
     if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
         if request.method == 'POST' :
            if 'file' not in request.files:
                flash('No file part')
                return "A file is missing"
            file = request.files['file']
            try:
                df=pd.read_csv(file)
            except:
                return "Could not convert csv file."
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], iden + '_data.csv'))
            return "Dataset uploaded successfully"
         elif request.method == 'GET' :
            return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), iden + '_data.csv', as_attachment=True)
         else:
            return "The only supported actions for this request are POST and GET"

     return "The model with the provided id doesn't exist"


@app.route('/delete', methods=['DELETE'])
def delete_model():
    iden = request.form.get('id')
    if iden is None:
        flash('No id part')
        return "The model id is missing"
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if request.method == 'DELETE':
            try:
                shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER'], iden))
            except:
                return "Model folder could not be deleted."
            return "Model folder deleted successfully"
        return "The only supported action for this request is DELETE."
    return "The id does not exist."

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

@app.route('/predict', methods=['POST'])
def predict():
    iden = request.form.get('id')
    if iden is None:
        flash('No id part')
        return "The model id is missing"
    if(not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        return "The id does not exists."
    with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
        model_info=json.load(f)
    
    url=""
    if model_info["backend"] in URLS:
        url=url+URLS[model_info["backend"]]+"/"
    else:
        return "The prediction resource currently does not support " +model_info["backend"]+ " models."
    if model_info["dataset_type"] in DATASET_TYPES:
        url=url+model_info["dataset_type"]+"/"
    else:
        return "The prediction resource currently does not support " +model_info["dataset_type"]+ " dataset types."
    url=url+"run"

    payload={"id": iden}
    files={}
    instance=request.form.get('instance')
    image = request.files.get('image', None)
    top_classes=request.form.get('top_classes')
    
    if instance==None:
        if model_info["dataset_type"].lower()=="image" and image!=None:
            files["image"]=image
        else:
            return "No instance or image was provided."
    else:
        payload["instance"]=instance

    try:
        top_classes=int(top_classes)
    except:
        top_classes='all'
    payload["top_classes"]=top_classes
   
    response = requests.post(url,data=payload,files=files,verify=False)
   
    if not response.ok:
      return "REQUEST FAILED:\nURL Request: " + url + "\nURL Response: " + str(response.url) +"\ndata:" + str(payload)+"\nheaders: " +str(response.request.headers) +"\nReason: " + str(response.status_code) + " " + str(response.reason)
    
    res=response.text
    try:
        res=json.loads(response.text)
    except:
        #An error occurred
        pass
    return res

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000)
