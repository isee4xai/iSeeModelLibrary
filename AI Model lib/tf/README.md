# Model Library (TensorFlow)

The following document will explain how to call the various functions implemented in the model library API for the iSee project, in particular we will describe the behaviour for the TensorFlow version.

## Basic functions

### Uploading a model

In order to upload a model to the API the function `upload_model` must be called in `POST` mode using the following parameters in the Body **form-data** section:

-  `file`:  this field must contain a the model that we wish to upload.
- `params`: this field must contain a json formatted text with the various properties of the model.
- `id`(**optional**): this field contains the id which will be used to refer to the uploaded model in the rest of the functions. If it is left blank a random id will be assigned.

The function will return the **id** assigned to the model.

*Here we have an example using Postman:*

![Uploading a model](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/tf/img/upload_model.PNG?raw=true)

### Updating a model

In order to update an existing model to the API the function `upload_model` must be called in `PUT` mode using the following parameters in the Body **form-data** section:

-  `file`:  this field must contain a the model that we wish to update.
- `params`: this field must contain a json formatted text with the various properties of the model.
- `id`: this field must contain the id of the model that we wish to update.

The function will return a message confirming the update of the model.

*Here we have an example using Postman:*

![Updating a model](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/tf/img/Update.PNG?raw=true)

### Uploading a dataset

In order to upload a model to the API the function `dataset` must be called in `POST` mode using the following parameters in the Body **form-data** section:

-  `file`:  this field must contain a *.pkl* file which corresponds to the dataset that we want to upload.
- `id`: this field must contain the id of the model whose dataset we are uploading.

The function will return a message confirming the upload of the dataset.

*Here we have an example using Postman:*

![Uploading a dataset](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/tf/img/add_dataset.PNG?raw=true)

### Retrieve a dataset

In order to obtain the dataset used to train a model from  the API the function `dataset` must be called in `GET` mode using the following parameters in the **URL parameter** section:
- `id`: this field must contain the id of the model whose dataset we wish to retrieve.

The function will return the dataset associated with the id.

*Here we have an example using Postman:*

![Uploading a dataset](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/tf/img/return_dataset.PNG?raw=true)

### Deleting a model

In order to delete an uploaded model from the API the function `delete` must be called in `DELETE` mode using the following parameters in the Body **form-data** section:

- `id`: this field must contain the id of the model we wish to delete.

The function will return a message confirming the deletion.

*Here we have an example using Postman:*

![Uploading a dataset](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/tf/img/delete_model.PNG?raw=true)

### Retrieving a model's parameters

In order to retrieve the parameters provided when uploading a model to the API the function `info` must be called in `GET` mode using the following parameters in the **URL parameter** section:

- `id`: this field must contain the id of the model whose parameters we wish to retrieve.

The function will return a json with the parameters.

*Here we have an example using Postman:*

![Uploading a dataset](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/tf/img/get_model_params.PNG?raw=true)

### Predicting with an image

In order to make a prediction based on an image using a model uploaded to the API the function `/Image/run` must be called in `POST` mode using the following parameters in the Body **form-data** section:

-  `image`:  this field must contain a file which corresponds to the image that we want to pass to the model.
- `id`: this field must contain the id of the model that we want to use to make the prediction.

The function will return a message with the model prediction.


*Here we have an example using Postman:*

![Uploading a dataset](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/tf/img/predict_img.PNG?raw=true)

### Predicting with a tabular set

In order to make a prediction based on a dataset using a model uploaded to the API the function `/Tabular/run` must be called in `POST` mode using the following parameters in the Body **form-data** section:

-  `data`:  this field must contain a text formatted as a json with a field named *"instance"* followed by an array containing the data to be passed to the model.
- `id`: this field must contain the id of the model that we want to use to make the prediction.

The function will return a message with the model prediction.


*Here we have an example using Postman:*

![Uploading a dataset](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/tf/img/predict_tab_1.PNG?raw=true)
