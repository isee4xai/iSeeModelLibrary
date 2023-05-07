import sys
import pathlib
from flask import Flask, send_from_directory,request, json, jsonify
from flask_restful import Api
import tensorflow as tf
import pandas as pd
import numpy as np
import markdown
import markdown.extensions.fenced_code
import os
from flask import Flask, flash, request
from utils.base64 import base64_to_vector
from utils.img_processing import normalize_img
from utils.dataframe_processing import normalize_dataframe, normalize_dict
from utils import ontologyConstants

UPLOAD_FOLDER = 'Models'
ALLOWED_EXTENSIONS = {'h5'}
EXTENSION = '.h5'
NOT_ALLOWED_SYMBOLS = {'<', '>', ':', '\"', '/', '\\', '|', '\?', '*', '\''}

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

#def allowed_file(filename):
#    return '.' in filename and \
#           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#def allowed_id(iden):
#    for c in NOT_ALLOWED_SYMBOLS:
#        if c in iden:
#            return False
#    return True

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
#                json.dump(parameters, f)
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

    #Check params
    params_str = request.form.get('params')
    if params_str is None:
        flash('No params part')
        return "The params are missing"
    params={}
    try:
        params = json.loads(params_str)
    except Exception as e:
        return "Could not convert params to JSON: " + str(e)

    if("id" not in params):
        return "The model id was not specified in the params."
    if("type" not in params):
        return "The instance type was not specified in the params."
    if("instance" not in params):
        return "The instance was not specified in the params."
    if("top_classes" not in params):
        return "The top_classes parameter was not specified."
    iden=params["id"]
    inst_type=params["type"]
    if(inst_type=="dict"):
        instance=json.loads(params["instance"])
    elif(inst_type=="image"):
        instance=params["instance"]
    top_classes=params["top_classes"]
    if(params["top_classes"]!='all'):
        top_classes=int(params["top_classes"])

    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if request.method == 'POST':
            model = tf.keras.models.load_model(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".h5"), compile=False)
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
                model_info=json.load(f)

            #converting to vector
            try:
                instance=base64_to_vector(instance)
            except Exception as e:  
                return "Could not convert base64 Image to vector: " + str(e)

            #normalizing
            try:
                instance=normalize_img(instance,model_info)
            except Exception as e:
                 return  "Could not normalize instance: " + str(e)

            try:
                predictions = model.predict(instance)[0].tolist()
                print(predictions)
            except Exception as e:
                return "Could not execute predict function:" + str(e)
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
                                return "Could not convert top_classes argument to integer. If you want predictions for all the classes set top_classes to 'all'."
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
                    return "AI model task not supported."

                return jsonify(ret)
            except Exception as e:
                print(e)
                print(instance.shape)
                return "Something went wrong"
        return "The only supported action for this request is POST"
    return "The model does not exist"


@app.route('/Tabular/run', methods=['POST'])
def run_tab_model():
    #Check params
    params_str = request.form.get('params')
    if params_str is None:
        flash('No params part')
        return "The params are missing"
    params={}
    try:
        params = json.loads(params_str)
    except Exception as e:
        return "Could not convert params to JSON: " + str(e)

    if("id" not in params):
        return "The model id was not specified in the params."
    if("type" not in params):
        return "The instance type was not specified in the params."
    if("instance" not in params):
        return "The instance was not specified in the params."
    if("top_classes" not in params):
        return "The top_classes parameter was not specified."
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
            model = tf.keras.models.load_model(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".h5"), compile=False)
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
                model_info=json.load(f)
            if instance is None:
                flash('No instance part')
                return "No instance were provided"
            norm_inst=np.asarray([list(normalize_dict(instance,model_info).values())])
            try:
                tensor=tf.convert_to_tensor(norm_inst)
                predictions = model.predict(tensor)[0].tolist()
            except Exception as e:
                return "Could not execute predict function:" + str(e)
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
                                return "Could not convert top_classes argument to integer. If you want predictions for all the classes set top_classes to 'all'."
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
                    return "AI model task not supported."

                return jsonify(ret)
            except Exception as e:
                print(e)
                return "Something went wrong: " + str(e)
        return "The only supported action for this request is POST"
    return "The model does not exist"

@app.route('/Text/run', methods=['POST'])
def run_text_model():
    iden = request.form.get('id')
    if iden is None:
        flash('No params part')
        return "The model id is missing"
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        data = request.form.get('instance')
        if request.method == 'POST':
            model = tf.keras.models.load_model(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".h5"), compile=False)
            if data is None:
                flash('No instances part')
                return "No instances were provided"
            X=data
            try:
                data=json.loads(data)
                X = np.asarray(data)
                if len(X.shape)==0:
                    X=X.reshape(1, -1)
            except:
                X=[X]
            try:
                predictions = model.predict(X)
                return jsonify({'predictions' : predictions.tolist()})
            except Exception as e:
                print(e)
                return "Something went wrong"
        return "The only supported action for this request is POST"
    return "The model does not exist"

@app.route('/Timeseries/run', methods=['POST'])
def run_time_model():
    #Check params
    params_str = request.form.get('params')
    if params_str is None:
        flash('No params part')
        return "The params are missing"
    params={}
    try:
        params = json.loads(params_str)
    except Exception as e:
        return "Could not convert params to JSON: " + str(e)

    if("id" not in params):
        return "The model id was not specified in the params."
    if("type" not in params):
        return "The instance type was not specified in the params."
    if("instance" not in params):
        return "The instance was not specified in the params."
    if("top_classes" not in params):
        return "The top_classes parameter was not specified."

    iden=params["id"]
    inst_type=params["type"]
    instance=params["instance"]
    top_classes=params["top_classes"]

    if(params["top_classes"]!='all'):
        top_classes=int(params["top_classes"])

    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if request.method == 'POST':
            model = tf.keras.models.load_model(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".h5"), compile=False)
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
                model_info=json.load(f)
            if instance is None:
                flash('No instance part')
                return "No instance were provided"

            target_names=model_info["attributes"]["target_names"]
            features=model_info["attributes"]["features"]
            feature_names=list(features.keys())
            time_feature=None
            for feature, info_feature in features.items():
                if(info_feature["data_type"]=="time"):
                    time_feature=feature
                    break

            df_instance=pd.DataFrame(instance,columns=feature_names).drop([time_feature], axis=1, errors='ignore')

            try:
                norm_instance=np.expand_dims(normalize_dataframe(df_instance, model_info).to_numpy(),axis=0)
                tensor=tf.convert_to_tensor(norm_instance)
                predictions = np.squeeze(model.predict(tensor)).tolist()
            except Exception as e:
                 print("Could not execute predict function including target columns in instance:" + str(e))
                 try:
                     df_instance.drop(target_names,axis=1,inplace=True)
                     norm_instance=np.expand_dims(normalize_dataframe(df_instance, model_info).to_numpy(),axis=0)
                     tensor=tf.convert_to_tensor(norm_instance)
                     predictions = np.squeeze(model.predict(tensor)).tolist()
                 except Exception as e:
                    return "Could not execute predict function:" + str(e) 

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
                                return "Could not convert top_classes argument to integer. If you want predictions for all the classes set top_classes to 'all'."
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
                    return "AI model task not supported."

                return jsonify(ret)
            except Exception as e:
                print(e)
                return "Something went wrong: " + str(e)
        return "The only supported action for this request is POST"
    return "The model does not exist"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
