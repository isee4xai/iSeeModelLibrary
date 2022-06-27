

# Model Library (generic)

The following document will explain the various functions needed to implement in order to communicate with the model library API for the iSee project.

## Requirements


The client must implement the following capabilities:

### Retrieving a model's parameters

In order to retrieve the parameters provided when uploading a model to the API the function `info` must be called in `GET` mode.

The function will return a json with the parameters.

*Here we have an example using Postman:*

![Retrieving a model's parameters](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/img/get_model_param.PNG?raw=true)


### Retrieve a dataset (optional)

In order to obtain the dataset used to train a model from the API the function `dataset` must be called in `GET` mode.

The function will return the dataset associated with the model.

*Here we have an example using Postman:*

![Retrieving a model's dataset](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/img/get_dataset.PNG?raw=true)

### Predicting with an image

If the model uses images as input, in order to make a prediction based on an image using a model uploaded to the API the function `/Image/run` must be called in `POST` mode using the following parameters in the Body **form-data** section:

-  `image`:  this field must contain a file which corresponds to the image that we want to pass to the model.

The function will return a message with the model prediction.


*Here we have an example using Postman:*

![Predicting an image](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/img/predict_image.PNG?raw=true)

### Predicting with a tabular set

If the model uses a dataset as input, in order to make a prediction based on a dataset using a model uploaded to the API the function `/Tabular/run` must be called in `POST` mode using the following parameters in the Body **form-data** section:

-  `data`:  this field must contain a text formatted as a json with a field named *"instance"* followed by an array containing the data to be passed to the model.

The function will return a message with the model prediction.

*Here we have an example using Postman:*

![Predicting with a dataset](https://github.com/isee4xai/iSeeBackend/blob/main/AI%20Model%20lib/img/predict_tab.PNG?raw=true)
