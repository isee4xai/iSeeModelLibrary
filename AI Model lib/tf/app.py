import sys
import pathlib
from flask import Flask, send_from_directory,request, json, jsonify
from flask_restful import Api
import tensorflow as tf
import numpy as np
import markdown
import markdown.extensions.fenced_code
from PIL import Image
import os
from flask import Flask, flash, request


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
    iden = request.form.get('id')
    if iden is None:
        flash('No id part')
        return "The model id is missing"
    if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], iden))):
        if request.method == 'POST':
            model = tf.keras.models.load_model(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".h5"), compile=False)
            with open(os.path.join(app.config['UPLOAD_FOLDER'], iden, iden + ".json")) as f:
                model_info=json.load(f)
            instance=request.form.get('instance')
            top_classes=request.form.get('top_classes')
            #From Image file
            if instance==None:
                if 'image' not in request.files:
                    flash('No image part')
                    return "No image was provided"
                image = request.files['image']
                im=Image.open(image)
                #cropping
                shape_raw=model_info["attributes"]["features"]["image"]["shape_raw"]
                if(im.width<shape_raw[0] or im.height<shape_raw[1]):
                    return "The image is too small."
                im=im.crop(((im.width-shape_raw[0])/2,(im.height-shape_raw[1])/2,(im.width+shape_raw[0])/2,(im.height+shape_raw[1])/2))
                instance=np.asarray(im)
                #normalizing
                nmin=model_info["attributes"]["features"]["image"]["min"]
                nmax=model_info["attributes"]["features"]["image"]["max"]
                min_raw=model_info["attributes"]["features"]["image"]["min_raw"]
                max_raw=model_info["attributes"]["features"]["image"]["max_raw"]
                try:
                    instance=((instance-min_raw) / (max_raw - min_raw)) * (nmax - nmin) + nmin
                except:
                    return "Could not normalize instance."
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
            try:
                predictions = model.predict(instance)[0].tolist()
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
                flash('No instance part')
                return "No instances were provided"
            instance = json.loads(instance)
            instance = np.asarray(instance)
            if len(instance.shape)==1:
                 instance=instance.reshape(1, -1)
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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
