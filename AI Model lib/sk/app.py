from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR
import sys
import pathlib
from flask import Flask, send_from_directory,request, json, jsonify
from flask_restful import Api
import numpy as np
import joblib
from sklearn.base import is_classifier
import pandas as pd
import markdown
import markdown.extensions.fenced_code
from PIL import Image
import os
from flask import Flask, flash, request
from utils.dataframe_processing import normalize_dataframe
from utils import ontologyConstants

UPLOAD_FOLDER = 'Models'
ALLOWED_EXTENSIONS = {'pkl'}
EXTENSION = '.pkl'
NOT_ALLOWED_SYMBOLS = {'<', '>', ':', '\"', '/', '\\', '|', '\?', '*'}


cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None
app = Flask(__name__)
api = Api(app)
app_path = pathlib.Path(__file__).parent.absolute()

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
                UPLOAD_FOLDER = sys.argv[1]
            else:
                raise Exception("A non-directory file named '" + sys.argv[1]+ "' already exists. Please use another name.")
        else:
            os.mkdir(sys.argv[1])
            print("The '" +sys.argv[1]+ "' directory was created.")
            UPLOAD_FOLDER = sys.argv[1]

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    readme_file = open(str(app_path)+'/README.md', 'r')
    md_template_string = markdown.markdown(readme_file.read(), extensions=["fenced_code"])

    return md_template_string

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

def allowed_id(iden):
    for c in NOT_ALLOWED_SYMBOLS:
        if c in iden:
            return False
    return True

#@app.route('/upload_model', methods=['POST', 'PUT'])
#def upload_model():
#    #Add a new model to the server
#    if request.method == 'POST':
#        # check if the post request has the file part
#        if 'file' not in request.files:
#            flash('No file part')
#            return redirect(request.url)
#        parameters = request.form.get('params')
#        if parameters is None:
#            flash('No params part')
#            return redirect(request.url)
#        parameters = json.loads(parameters)
#        file = request.files['file']
#        # If the user does not select a file, the browser submits an
#        # empty file without a filename.
#        if file.filename == '':
#            flash('No selected file')   
#            return redirect(request.url)
#        if file and allowed_file(file.filename):
#            userid = request.form.get('id')
#            if userid is None or userid == '':
#                filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
#            else:
#                if allowed_id(userid):
#                    filename = userid
#                    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], userid)):
#                        return 'A model with the id: ' + userid + ' already exists'
#                else:
#                    return 'The provided id is invalid'
#            pathlib.Path(app.config['UPLOAD_FOLDER'], filename).mkdir(exist_ok=True)
#            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename, filename + EXTENSION))
#            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename ,filename + '.json'), 'w') as f:
#                json.dump(parameters, f, ensure_ascii = False)
#            return jsonify(
#                modelid = filename
#            )
#    #Update an existing model
#    elif request.method == 'PUT':
#        if 'file' not in request.files:
#            flash('No file part')
#            return 'A file hasnt been provided'

#        iden = request.form.get('id')
#        if iden is None:
#            flash('No id provided')
#            return "An id field is needed in order to update the model"

#        parameters = request.form.get('params')
#        if parameters is None:
#            flash('No params part')
#            return 'A param field is needed in order to update the model'
#        file = request.files['file']
#        parameters = json.loads(parameters)
#        if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
#            file.save(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + EXTENSION))
#            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden ,iden + '.json'), 'w') as f:
#                json.dump(parameters, f)
#            return "Model updated successfully"
#        else:
#            return "No model found with this id"

#    return '''
#    The only supported actions for this request are POST and PUT
#    '''

#@app.route('/dataset', methods=['POST', 'GET'])
#def dataset():   
#     if request.method == 'POST' :
#        iden = request.form.get('id')
#     elif request.method == 'GET':
#        iden = request.args.get('id')
#     else:
#        return "The only supported actions for this request are POST and GET" 
#     if iden is None:
#        flash('No params part')
#        return "The model id is missing"
#     if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
#         if request.method == 'POST' :
#            if 'file' not in request.files:
#                flash('No file part')
#                return "A file is missing"
#            file = request.files['file']
#            file.save(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '.pkl'))
#            return "Dataset uploaded successfully"
#         elif request.method == 'GET' :
#            return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), iden + '.pkl', as_attachment=True)
#         else:
#            return "The only supported actions for this request are POST and GET"

#     return "The model with the provided id doesn't exist"

#@app.route('/delete', methods=['DELETE'])
#def delete_model():
#    iden = request.form.get('id')
#    if iden is None:
#        flash('No params part')
#        return "The model id is missing"
#    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
#        if request.method == 'DELETE':
#            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + EXTENSION))
#            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '.json'))
#            if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '.pkl'))):
#                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + '.pkl'))
#            os.rmdir(os.path.join(app.config['UPLOAD_FOLDER'], iden))
#            return "Model deleted successfully"
#        return "The only supported action for this request is DELETE"
#    return "The model does not exist"

#@app.route('/info', methods=['GET'])
#def model_info():
#    iden = request.args.get('id')
#    if iden is None:
#        flash('No params part')
#        return "The model id is missing"
#    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
#        if request.method == 'GET':
#            return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], iden), iden + '.json', as_attachment=True)
#        return "The only supported action for this request is GET"
#    return "The model does not exist"

@app.route('/Image/run', methods=['POST'])
def run_img_model():
    iden = request.form.get('id')
    if iden is None:
        flash('No params part')
        return "The model id is missing",BAD_REQUEST
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if request.method == 'POST':
            model = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + EXTENSION))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
                model_info=json.load(f)
            instance=request.form.get('instance')
            if instance==None:
                if 'image' not in request.files:
                    flash('No image part')
                    return "No image was provided",BAD_REQUEST
                image = request.files['image']
                instance = np.asarray(Image.open(image))
            else:
                instance=np.asarray(json.loads(instance))
            if instance.shape!=tuple(model_info["attributes"]["features"]["image"]["shape"]):
                try:
                    instance = instance.reshape(tuple(model_info["attributes"]["features"]["image"]["shape"]))
                except:
                    return "Cannot reshape image of shape " + str(instance.shape) + " into shape " + str(tuple(model_info["attributes"]["features"]["image"]["shape"])),INTERNAL_SERVER_ERROR
            instance=instance.reshape((1,)+instance.shape)
            print(instance.shape)
            try:
                predictions = model.predict(instance)
                return jsonify({'predictions' : predictions.tolist()})
            except Exception as e:
                print(e)
                return "Something went wrong",INTERNAL_SERVER_ERROR

        return "The only supported action for this request is POST",BAD_REQUEST
    return "The model does not exist",BAD_REQUEST



@app.route('/Tabular/run', methods=['POST'])
def run_tab_model():
    
    #Check params
    params_str = request.form.get('params')
    if params_str is None:
        flash('No params part')
        return "The params are missing",BAD_REQUEST
    params={}
    try:
        params = json.loads(params_str)
    except Exception as e:
        return "Could not convert params to JSON: " + str(e),BAD_REQUEST

    if("id" not in params):
        return "The model id was not specified in the params.",BAD_REQUEST
    if("type" not in params):
        return "The instance type was not specified in the params.",BAD_REQUEST
    if("instance" not in params):
        return "The instance was not specified in the params.",BAD_REQUEST
    if("top_classes" not in params):
        return "The top_classes parameter was not specified.",BAD_REQUEST
    iden=params["id"]
    inst_type=params["type"]
    if(inst_type=="dict"):
        instance=params["instance"]
    elif(inst_type=="image"):
        instance=params["instance"]
    top_classes=params["top_classes"]
    if(params["top_classes"]!='all'):
        top_classes=int(params["top_classes"])

    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if request.method == 'POST':
            model = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + EXTENSION))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
                model_info=json.load(f)
            if instance is None:
                flash('No instance part')
                return "No instance were provided",BAD_REQUEST

            if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv"))): 
                    dataframe=pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv"),header=0)
            else:
                return "No training data was uploaded for this model.",BAD_REQUEST

            target_names=model_info["attributes"]["target_names"]
            feature_names=list(dataframe.columns)
            for target in target_names:
                feature_names.remove(target)

            #normalize instance
            df_inst=pd.DataFrame([instance.values()],columns=instance.keys())
            df_inst=df_inst[feature_names]
            norm_inst=normalize_dataframe(df_inst,model_info).to_numpy()

            try:
                 #if it's a classification model we try to launch predict_proba
                if is_classifier(model):
                    try:
                        predictions = model.predict_proba(norm_inst)                   
                    except Exception as e:
                        predictions = model.predict(norm_inst)
                else:
                    predictions = model.predict(norm_inst)
                predictions=np.squeeze(np.array(predictions)).tolist()
            except Exception as e:
                print(e)
                return "Could not execute predict function",INTERNAL_SERVER_ERROR
            try:
                ret={}
                print(predictions)
                multi=len(model_info["attributes"]["target_names"])!=1
                i=0
                #Classification
                if(model_info["model_task"] in ontologyConstants.CLASSIFICATION_URIS):
                    
                    for target_name in model_info["attributes"]["target_names"]:
                        label=model_info["attributes"]["features"][target_name]
                        preds_dict={}
                        if(top_classes!='all'):
                            try:
                                top_classes=min(int(top_classes),np.array(predictions).shape[-1])
                            except Exception as e:
                                print(e)
                                return "Could not convert top_classes argument to integer. If you want predictions for all the classes set top_classes to 'all'.",INTERNAL_SERVER_ERROR
                        else:
                            top_classes=np.array(predictions).shape[-1]

                        if multi:
                            preds=predictions[i]
                        else:
                            preds=predictions

                        for j in range(top_classes):
                            top_index=np.argmax(preds)
                            preds_dict[label["values_raw"][top_index]]=round(predictions[top_index],3)
                            preds.pop(top_index)
                            label["values_raw"].pop(top_index)
                        
                        if multi:
                            ret[target_name]=preds_dict
                        else: 
                            ret=preds_dict
                        i=i+1
                #Regression
                elif (model_info["model_task"] in ontologyConstants.REGRESSION_URIS):

                    for target_name in model_info["attributes"]["target_names"]:
                        if multi:
                            ret[target_name]=predictions[i]
                        else: 
                            ret[target_name]=predictions
                        i=i+1
                else:
                    return "AI model task not supported.",BAD_REQUEST

                return jsonify(ret)
            except Exception as e:
                print(e)
                return "Something went wrong: " + str(e),INTERNAL_SERVER_ERROR
        return "The only supported action for this request is POST",BAD_REQUEST
    return "The model does not exist",BAD_REQUEST

@app.route('/Text/run', methods=['POST'])
def run_text_model():

    #Check params
    params_str = request.form.get('params')
    if params_str is None:
        flash('No params part')
        return "The params are missing",BAD_REQUEST
    params={}
    try:
        params = json.loads(params_str)
    except Exception as e:
        return "Could not convert params to JSON: " + str(e),BAD_REQUEST

    if("id" not in params):
        return "The model id was not specified in the params.",BAD_REQUEST
    if("type" not in params):
        return "The instance type was not specified in the params.",BAD_REQUEST
    if("instance" not in params):
        return "The instance was not specified in the params.",BAD_REQUEST
    if("top_classes" not in params):
        return "The top_classes parameter was not specified.",BAD_REQUEST

    iden=params["id"]
    inst_type=params["type"]
    instance=params["instance"]
    top_classes=params["top_classes"]

    if(params["top_classes"]!='all'):
        top_classes=int(params["top_classes"])

    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if request.method == 'POST':
            model = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + EXTENSION))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
                model_info=json.load(f)
            norm_inst=np.array([instance])
            print(norm_inst)
            try:
                 # we try to launch predict_proba
                if callable(getattr(model, "predict_proba", None)):
                    try:
                        predictions = model.predict_proba(norm_inst)       
                        print(predictions)
                    except Exception as e:
                        predictions = model.predict(norm_inst)
                else:
                    predictions = model.predict(norm_inst)
                predictions=np.squeeze(np.array(predictions)).tolist()
            except Exception as e:
                print(e)
                return "Could not execute predict function",INTERNAL_SERVER_ERROR
            try:
                ret={}
                print(predictions)
                multi=len(model_info["attributes"]["target_names"])!=1
                i=0
                #Classification
                if(model_info["model_task"] in ontologyConstants.CLASSIFICATION_URIS):
                    
                    for target_name in model_info["attributes"]["target_names"]:
                        label=model_info["attributes"]["features"][target_name]
                        preds_dict={}
                        if(top_classes!='all'):
                            try:
                                top_classes=min(int(top_classes),np.array(predictions).shape[-1])
                            except Exception as e:
                                print(e)
                                return "Could not convert top_classes argument to integer. If you want predictions for all the classes set top_classes to 'all'.",INTERNAL_SERVER_ERROR
                        else:
                            top_classes=np.array(predictions).shape[-1]

                        if multi:
                            preds=predictions[i]
                        else:
                            preds=predictions

                        for j in range(top_classes):
                            top_index=np.argmax(preds)
                            preds_dict[label["values_raw"][top_index]]=round(predictions[top_index],3)
                            preds.pop(top_index)
                            label["values_raw"].pop(top_index)
                        
                        if multi:
                            ret[target_name]=preds_dict
                        else: 
                            ret=preds_dict
                        i=i+1
                #Regression
                elif (model_info["model_task"] in ontologyConstants.REGRESSION_URIS):

                    for target_name in model_info["attributes"]["target_names"]:
                        if multi:
                            ret[target_name]=predictions[i]
                        else: 
                            ret[target_name]=predictions
                        i=i+1
                else:
                    return "AI model task not supported.",BAD_REQUEST

                return jsonify(ret)
            except Exception as e:
                print(e)
                return "Something went wrong",INTERNAL_SERVER_ERROR
        return "The only supported action for this request is POST",BAD_REQUEST
    return "The model does not exist",BAD_REQUEST

@app.route('/Timeseries/run', methods=['POST'])
def run_time_model():
    #Check params
    params_str = request.form.get('params')
    if params_str is None:
        flash('No params part')
        return "The params are missing",BAD_REQUEST
    params={}
    try:
        params = json.loads(params_str)
    except Exception as e:
        return "Could not convert params to JSON: " + str(e),BAD_REQUEST

    if("id" not in params):
        return "The model id was not specified in the params.",BAD_REQUEST
    if("type" not in params):
        return "The instance type was not specified in the params.",BAD_REQUEST
    if("instance" not in params):
        return "The instance was not specified in the params.",BAD_REQUEST
    if("top_classes" not in params):
        return "The top_classes parameter was not specified.",BAD_REQUEST

    iden=params["id"]
    inst_type=params["type"]
    instance=params["instance"]
    top_classes=params["top_classes"]

    if(params["top_classes"]!='all'):
        top_classes=int(params["top_classes"])

    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if request.method == 'POST':
            model = joblib.load(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + EXTENSION))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
                model_info=json.load(f)
            if instance is None:
                flash('No instance part')
                return "No instance were provided",BAD_REQUEST

            if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv"))): 
                    dataframe=pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + "_data.csv"),header=0)
            else:
                return "No training data was uploaded for this model.",BAD_REQUEST

            target_names=model_info["attributes"]["target_names"]
            features=model_info["attributes"]["features"]
            feature_names=list(dataframe.columns)
            time_feature=None
            for feature, info_feature in features.items():
                if(info_feature["data_type"]=="time"):
                    time_feature=feature
                    break

            if (model_info["dataset_type"]==ontologyConstants.TIMESERIES_URIS[0]): #multivariate

                df_instance=pd.DataFrame(instance,columns=feature_names).drop([time_feature], axis=1, errors='ignore')
                df_instance=df_instance[feature_names]

                try:
                    norm_instance=np.expand_dims(normalize_dataframe(df_instance, model_info).to_numpy(),axis=0)
                    predictions = np.squeeze(model.predict(norm_instance)).tolist()
                except Exception as e:
                     print("Could not execute predict function including target columns in instance:" + str(e))
                     try:
                         df_instance.drop(target_names,axis=1,inplace=True)
                         norm_instance=np.expand_dims(normalize_dataframe(df_instance, model_info).to_numpy(),axis=0)
                         predictions = np.squeeze(model.predict(norm_instance)).tolist()
                     except Exception as e:
                        return "Could not execute predict function:" + str(e),INTERNAL_SERVER_ERROR
            else: #univariate
                norm_instance=np.expand_dims(np.array(instance),axis=0)

                                 # we try to launch predict_proba
                if callable(getattr(model, "predict_proba", None)):
                    try:
                        predictions=np.squeeze(model.predict_proba(norm_instance)).tolist()     
                    except Exception as e:
                        predictions=np.squeeze(model.predict(norm_instance)).tolist()

            try:
                ret={}
                print(predictions)
                multi=len(model_info["attributes"]["target_names"])!=1
                i=0
                #Classification
                if(model_info["model_task"] in ontologyConstants.CLASSIFICATION_URIS):
                    
                    for target_name in model_info["attributes"]["target_names"]:
                        label=model_info["attributes"]["features"][target_name]
                        preds_dict={}
                        if(top_classes!='all'):
                            try:
                                top_classes=min(int(top_classes),np.array(predictions).shape[-1])
                            except Exception as e:
                                print(e)
                                return "Could not convert top_classes argument to integer. If you want predictions for all the classes set top_classes to 'all'.",BAD_REQUEST
                        else:
                            top_classes=np.array(predictions).shape[-1]

                        if multi:
                            preds=predictions[i]
                        else:
                            preds=predictions

                        for j in range(top_classes):
                            top_index=np.argmax(preds)
                            preds_dict[label["values_raw"][top_index]]=round(predictions[top_index],3)
                            preds.pop(top_index)
                            label["values_raw"].pop(top_index)
                        
                        if multi:
                            ret[target_name]=preds_dict
                        else: 
                            ret=preds_dict
                        i=i+1
                #Regression
                elif (model_info["model_task"] in ontologyConstants.REGRESSION_URIS):

                    for target_name in model_info["attributes"]["target_names"]:
                        if multi:
                            ret[target_name]=predictions[i]
                        else: 
                            ret[target_name]=predictions
                        i=i+1
                else:
                    return "AI model task not supported.",BAD_REQUEST

                return jsonify(ret)
            except Exception as e:
                print(e)
                return "Something went wrong: " + str(e),INTERNAL_SERVER_ERROR
        return "The only supported action for this request is POST",BAD_REQUEST
    return "The model does not exist",BAD_REQUEST

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
