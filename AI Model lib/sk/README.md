# Model Library (sklearn)

The following document will explain how to call the various functions implemented in the model library API for the iSee project, in particular we will describe the behaviour for the sklearn version.

## Basic functions

### Uploading a model

In order to upload a model to the API the function `upload_model` must be called in `POST` mode using the following parameters in the Body **form-data** section:

-  `file`:  this field must contain a the model that we wish to upload.
- `params`: this field must contain a json formatted text with the various properties of the model.
- `id`(**optional**): this field contains the id which will be used to refer to the uploaded model in the rest of the functions. If it is left blank a random id will be assigned.

The function will return the **id** assigned to the model.

### Updating a model

In order to update an existing model to the API the function `upload_model` must be called in `PUT` mode using the following parameters in the Body **form-data** section:

-  `file`:  this field must contain a the model that we wish to update.
- `params`: this field must contain a json formatted text with the various properties of the model.
- `id`: this field must contain the id of the model that we wish to update.

The function will return a message confirming the update of the model.

### Uploading a dataset

In order to upload a model to the API the function `dataset` must be called in `POST` mode using the following parameters in the Body **form-data** section:

-  `file`:  this field must contain a *.pkl* file which corresponds to the dataset that we want to upload.
- `id`: this field must contain the id of the model whose dataset we are uploading.

The function will return a message confirming the upload of the dataset.

### Retrieve a dataset

In order to obtain the dataset used to train a model from the API the function `dataset` must be called in `GET` mode using the following parameters in the **URL parameter** section:
- `id`: this field must contain the id of the model whose dataset we wish to retrieve.

The function will return the dataset associated with the id.

### Deleting a model

In order to delete an uploaded model from the API the function `delete` must be called in `DELETE` mode using the following parameters in the Body **form-data** section:

- `id`: this field must contain the id of the model we wish to delete.

The function will return a message confirming the deletion.

### Retrieving a model's parameters

In order to retrieve the parameters provided when uploading a model to the API the function `info` must be called in `GET` mode using the following parameters in the **URL parameter** section:

- `id`: this field must contain the id of the model whose parameters we wish to retrieve.

The function will return a json with the parameters.

### Predicting with an image

In order to make a prediction based on an image using a model uploaded to the API the function `/Image/run` must be called in `POST` mode using the following parameters in the Body **form-data** section:

-  `image`:  this field must contain a file which corresponds to the image that we want to pass to the model.
- `id`: this field must contain the id of the model that we want to use to make the prediction.

The function will return a message with the model prediction.

### Predicting with a tabular set

In order to make a prediction based on a dataset using a model uploaded to the API the function `/Tabular/run` must be called in `POST` mode using the following parameters in the Body **form-data** section:

-  `data`:  this field must contain a text formatted as a json with a field named *"instance"* followed by an array containing the data to be passed to the model.
- `id`: this field must contain the id of the model that we want to use to make the prediction.

The function will return a message with the model prediction.
