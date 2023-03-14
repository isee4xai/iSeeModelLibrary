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
from utils import ontologyConstants
from utils.base64 import vector_to_base64,PIL_to_base64
from utils.img_processing import denormalize_img
from utils.dataframe_processing import denormalize_dataframe

from timeit import default_timer as timer
from datetime import datetime

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


SKLEARN_SERVER="http://models-sk:5000"
TENSORFLOW_SERVER="http://models-tf:5000"


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
        if(model_info["dataset_type"] in ontologyConstants.IMAGE_URIS):
            #from image folder
            folder_path=os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data")
            if(os.path.exists(folder_path)):
                nfiles=sum([len(files) for r, d, files in os.walk(folder_path)])
                if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data", model_info["attributes"]["target_names"][0]+".csv"))):
                   nfiles=nfiles-1
                return {"count":nfiles}
            #from .csv
            elif(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv"))): 
                with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv")) as f:
                    return {"count":sum(1 for line in f)-1}
            else:
                return "No training data was uploaded for this model."
        #For Tabular or Text
        elif(model_info["dataset_type"] in ontologyConstants.TABULAR_URIS or model_info["dataset_type"] in ontologyConstants.TEXT_URIS):
            if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv"))): 
                with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv")) as f:
                    return {"count":sum(1 for line in f)-1}
            else:
                return "No training data was uploaded for this model."
    else:
        return "The model does not exist."


@app.route('/view_image/<string:iden>/<string:filename>',methods=['GET'])
def view_image(iden, filename):
    if iden is None:
        flash('No id part')
        return "The model id is missing."
    if filename is None:
        flash('No filename part')
        return "The filename is missing."
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, filename)):
        return "The file does not exist"
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), filename)


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
        if(model_info["dataset_type"] in ontologyConstants.IMAGE_URIS):

            #from image folder
            folder_path=os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data")
            if(os.path.exists(folder_path)):  
                extrafile=0
                if(os.path.exists(os.path.join(folder_path,model_info["attributes"]["target_names"][0]+".csv"))):
                    extrafile=1

                img_path=None
                i=0
                found=False
                for dirpath,_,filenames in os.walk(folder_path):
                    for f in filenames:
                        if i==index:
                            img_path=os.path.abspath(os.path.join(dirpath, f))
                            found=True
                            break
                        i=i+1
                    if found:
                        break
                if(img_path is None):
                    return "The index is invalid."

                im=None
                try:
                    im=Image.open(img_path)
                except Exception as e:
                    return "Could not open image file with PIL: " + str(e)

                try:
                    b64Image=PIL_to_base64(im)
                except Exception as e:
                    return "Could not convert PIL image to base64: " + str(e)

                #returning dict
                ret={"type":"image", "instance":b64Image,"size_raw":list(model_info["attributes"]["features"]["image"]["shape_raw"][0:2])}
                return ret

            #from csv
            elif(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv"))): 
                instance=None
                start = timer()
                with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv"), 'r') as f:
                    header=next(f).split(',')
                    header=[elem.strip() for elem in header]
                    label_indexes=[]
                    for target_name in model_info["attributes"]["target_names"]:
                        label_indexes.append(header.index(target_name))
                    for i in range(index):
                        try:
                            next(f)
                        except Exception as e:
                           print(e)
                           return "Index out of bounds."       
                    try:
                        string=next(f)
                    except Exception as e:
                        print(e)
                        return "Index out of bounds."
                    array_str=string.split(',')
                    for i in label_indexes:
                        array_str.pop(i) #remove label column
                    array_str.pop(0) ##remove row number column
                    instance=np.asarray(array_str, dtype=float)
                end = timer()
                print("Getting instance time: " + str(round(end - start,2)) + " s") 

                #denormalizing
                try:
                    instance=denormalize_img(instance,model_info)
                except Exception as e:
                    return "Could not denormalize instance: " + str(e)
                
                #converting to base64 Image
                b64Image=None
                try:
                    b64Image=vector_to_base64(instance)
                except Exception as e:
                    return "Could not convert instance to base64 Image: " + str(e)
               
                #returning dict
                ret={"type":"image", "instance":b64Image,"size_raw":list(model_info["attributes"]["features"]["image"]["shape_raw"][0:2])}
                return ret
          
            else:
                return "No training data was uploaded for this model."
        
        #For Tabular
        elif(model_info["dataset_type"] in ontologyConstants.TABULAR_URIS):

            if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.pkl"))):
                df = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.pkl"))
                try:
                    target_names=model_info["attributes"]["target_names"]
                except Exception as e:
                    return "Could not extract target columns from model information. Please update the model attributes file: " + str(e)
                try:
                    df.drop(target_names, axis=1,inplace=True)
                except Exception as e:
                    return "Could not drop target feature/s: " + str(e)
                try:
                    instance=df.iloc[[index]]
                except Exception as e:
                    return "The index is invalid: " + str(e)
                try:
                    denorm_instance=denormalize_dataframe(instance,model_info)
                except Exception as e:
                    return "The instance could not be denormalized: " + str(e)
                instance=json.loads(denorm_instance.to_json(orient="table",index=False))["data"][0]
                return {"type":"dict","instance":instance,"size":len(instance)}
            else:
                return "The training dataset was not uploaded."

        elif(model_info["dataset_type"] in ontologyConstants.TEXT_URIS):

            if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.pkl"))):
                df = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.pkl"))
                try:
                    target_names=model_info["attributes"]["target_names"]
                except Exception as e:
                    return "Could not extract target columns from model information. Please update the model attributes file: " + str(e)
                try:
                    df.drop(target_names, axis=1,inplace=True)
                except Exception as e:
                    return "Could not drop target feature/s: " + str(e)
                try:
                    instance=df.iloc[[index]]
                except Exception as e:
                    return "The index is invalid: " + str(e)
                text=instance.values[0][0]
                return {"type":"text","instance":text,"size":len(text)}
            else:
                return "The training dataset was not uploaded."
        else:
            return "The dataset type is not supported."
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

        if parameters["backend"] not in ontologyConstants.LIGHTGBM_URIS + ontologyConstants.PYTORCH_URIS + ontologyConstants.SKLEARN_URIS + ontologyConstants.TENSORFLOW_URIS + ontologyConstants.XGBOOST_URIS:
            return "Backend not supported."
        if parameters["dataset_type"] not in ontologyConstants.IMAGE_URIS + ontologyConstants.TABULAR_URIS + ontologyConstants.TEXT_URIS + ontologyConstants.TIMESERIES_URIS:
            return "Dataset type not supported."
        if parameters["model_task"] not in ontologyConstants.CLASSIFICATION_URIS + ontologyConstants.REGRESSION_URIS:
            return "Model task not supported."
        
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
            if(model_info["dataset_type"] in ontologyConstants.IMAGE_URIS):
                #zip file with images
                if(file.content_type=="application/zip"):
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".zip"))
                    folder_path_temp=os.path.join(app.config['UPLOAD_FOLDER'], iden, "temp")
                    os.makedirs(folder_path_temp,exist_ok=True)
                    with zipfile.ZipFile(file) as zip_ref:
                            zip_ref.extractall(folder_path_temp)
                    filename=file.filename.split(".zip")[0]
                    if(filename not in os.listdir(folder_path_temp)):
                        filename=""
                    if(model_info["model_task"] in ontologyConstants.CLASSIFICATION_URIS): 
                        if set(os.listdir(folder_path_temp+'/'+filename))!=set(model_info["attributes"]["features"][model_info["attributes"]["target_names"][0]]["values_raw"]):
                            shutil.rmtree(folder_path_temp)
                            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".zip"))
                            return "The names of the subfolders in the zipped file do not match the names of the output classes."
                    elif(model_info["model_task"] in ontologyConstants.REGRESSION_URIS): 
                        if(not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden,folder_path_temp,filename, model_info["attributes"]["target_names"][0]+".csv"))):
                            shutil.rmtree(folder_path_temp)
                            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".zip"))
                            return "There is no target .csv file with the regression values."
                    folder_path=os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data")
                    if os.path.exists(folder_path):
                        shutil.rmtree(folder_path)
                    os.rename(os.path.join(folder_path_temp,filename),folder_path)
                    shutil.rmtree(folder_path_temp)
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
            #For Tabular and Text
            elif(model_info["dataset_type"] in ontologyConstants.TABULAR_URIS or model_info["dataset_type"] in ontologyConstants.TEXT_URIS):
                if(file.content_type=="text/csv"):
                    try:
                        df=pd.read_csv(file,header=0,index_col=0)
                        joblib.dump(df,os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '_data.pkl')) 
                        df.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '_data.csv'))
                    except Exception as e:
                        return "Could not convert .csv file to Pandas Dataframe: " +str(e)
                else:
                    return "The training data must be a .csv file."       
            else:
                return "The dataset type is not supported"
            return "Dataset uploaded successfully"
         elif request.method == 'GET' :
            if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '_data.csv'))):
                return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), iden + '_data.csv', as_attachment=True)
            elif (os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden+".zip"))):
                return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), iden + '.zip', as_attachment=True)
            else:
                return "No training file has been uploaded for this model."
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
    params = request.json
    if params is None:
        flash('No params part')
        return "The params are missing"

    #Check params
    if("id" not in params):
        return "The model id was not specified in the params."
    if("type" not in params):
        return "The instance type was not specified in the params."
    if("instance" not in params):
        return "The instance was not specified in the params."

    iden=params["id"]
    inst_type=params["type"]
    if(inst_type=="dict"):
        instance=params["instance"]
    elif(inst_type=="image"):
        instance=params["instance"]
    top_classes='all'
    try:
        top_classes=int(params["top_classes"])
    except:
        pass
        
    if(not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        return "The model id does not exists."
    with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
        model_info=json.load(f)
    
    url=""
    if model_info["backend"] in ontologyConstants.SKLEARN_URIS:
        url=url+SKLEARN_SERVER+"/"
    elif model_info["backend"] in ontologyConstants.TENSORFLOW_URIS:
        url=url+TENSORFLOW_SERVER+"/"
    else:
        return "The prediction resource currently does not support " +model_info["backend"].split("#")[-1]+ " models."

    if model_info["dataset_type"] in ontologyConstants.IMAGE_URIS:
        url=url+"Image/"
    elif model_info["dataset_type"] in ontologyConstants.TABULAR_URIS:
        url=url+"Tabular/"
    elif model_info["dataset_type"] in ontologyConstants.TEXT_URIS:
        url=url+"Text/"
    elif model_info["dataset_type"] in ontologyConstants.TIMESERIES_URIS:
        url=url+"Timeseries/"
    else:
        return "The prediction resource currently does not support " +model_info["dataset_type"].split("#")[-1]+ " dataset type."
    url=url+"run"

    payload={"params":json.dumps({"id": iden,"type":inst_type,"instance":instance,"top_classes":top_classes})}
    response = requests.post(url,data=payload,verify=False)
   
    if not response.ok:
      return "REQUEST FAILED:\nURL Request: " + url + "\nURL Response: " + str(response.url) +"\ndata:" + str(payload)+"\nheaders: " +str(response.request.headers) +"\nReason: " + str(response.status_code) + " " + str(response.reason)
    
    res=response.text
    try:
        res=json.loads(response.text)
    except:
        #An error occurred
        pass
    return res


@app.route('/predict_url', methods=['POST'])
def predict_url():
    iden = request.form.get('id')
    if iden is None:
        flash('No id part')
        return "The model id is missing"
    url= request.form.get('url')
    if url is None:
        flash('No url part')
        return "The url for the prediction function is missing"
    if(not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        return "The id does not exists."
    if(not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json"))):
        return "There is no configuration file for the id given."
    with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
        model_info=json.load(f)

    instance=request.form.get('instance')
    top_classes=request.form.get('top_classes','all')
    if (model_info["dataset_type"] in ontologyConstants.IMAGE_URIS):
        #From Image file
        if instance==None:
            if 'image' not in request.files:
                flash('No image part')
                return "No image was provided"
            image = request.files['image']
            im=Image.open(image)
            instance=np.asarray(im)
            #normalizing
            if("min" in model_info["attributes"]["features"]["image"] and "max" in model_info["attributes"]["features"]["image"] and
                "min_raw" in model_info["attributes"]["features"]["image"] and "max_raw" in model_info["attributes"]["features"]["image"]):
                nmin=model_info["attributes"]["features"]["image"]["min"]
                nmax=model_info["attributes"]["features"]["image"]["max"]
                min_raw=model_info["attributes"]["features"]["image"]["min_raw"]
                max_raw=model_info["attributes"]["features"]["image"]["max_raw"]
                try:
                    instance=((instance-min_raw) / (max_raw - min_raw)) * (nmax - nmin) + nmin
                except:
                    return "Could not normalize instance."
            elif("mean_raw" in model_info["attributes"]["features"]["image"] and "std_raw" in model_info["attributes"]["features"]["image"]):
                mean=np.array(model_info["attributes"]["features"]["image"]["mean_raw"])
                std=np.array(model_info["attributes"]["features"]["image"]["std_raw"])
                try:
                    instance=((instance-mean)/std).astype(np.uint8)
                except:
                    return "Could not normalize instance using mean and std dev."
        else:
            #From normalised array (can be flattened or have the expected shape)
            instance=np.asarray(json.loads(instance))
        if instance.shape!=tuple(model_info["attributes"]["features"]["image"]["shape"]):
            try:
                instance = instance.reshape(tuple(model_info["attributes"]["features"]["image"]["shape"]))
            except Exception as e:
                print(e)
                return "Cannot reshape image of shape " + str(instance.shape) + " into shape " + str(tuple(model_info["attributes"]["features"]["image"]["shape"]))
        instance=instance.reshape((1,)+instance.shape)
        def predict(X):
            try:
                ret=np.array(json.loads(requests.post(url, data=dict(inputs=str(X.tolist()))).text))
                return ret
            except Exception as e:
                print(e)
                return "Call to prediction function failed."      
        try:
            predictions = predict(instance)[0].tolist()
            preds_dict={}
            if(top_classes.lower()!='all'):
                try:
                    top_classes=min(int(top_classes),len(model_info["attributes"]["features"][model_info["attributes"]["target_names"][0]]["values_raw"]))
                except Exception as e:
                    print(e)
                    return "Could not convert top_classes argument to integer. If you want predictions for all the classes set top_classes to 'all'."
            else:
                top_classes=len(model_info["attributes"]["features"][model_info["attributes"]["target_names"][0]]["values_raw"])
            for i in range(top_classes):
                top_index=np.argmax(predictions)
                preds_dict[model_info["attributes"]["features"][model_info["attributes"]["target_names"][0]]["values_raw"][top_index]]=predictions[top_index]
                predictions.pop(top_index)
                model_info["attributes"]["features"][model_info["attributes"]["target_names"][0]]["values_raw"].pop(top_index)
            return jsonify(preds_dict)
        except Exception as e:
            print(e)
            print(instance.shape)
            return "Something went wrong"
    else:
        return "Datatype " + model_info["dataset_type"].split('#')[-1] + " is not yet supported for URL prediction"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000)
