const http = require('http')
const axios = require('axios');
const open = require('open');
const args = process.argv.slice(2);

//Variable declaration

let httpAddres = "http://localhost:3000/";
let httpAddresProjectsId = httpAddres + "Projects?id=";
let table = {};
let projectId = args[0];
let portCount = 8125;
let server_url = "http://192.168.1.34:5000";

//Obtaining the BT in JSON format.

var jsonData;
var root;
var modelid;
var exp_instance;

async function run(){
	await axios.get(httpAddresProjectsId + projectId).then(function (response) {
		jsonData = response.data[0].data.trees[0];
		//console.log(jsonData);
	  })
	  .catch(function (error) {
		console.log(error);
	  });
	root = jsonData.root;
	modelid = jsonData.idModel;
	exp_instance = jsonData.query;
	runNode(root);
}


//Here we need to call a function to make sure the data.json contains the necessary parameters.
//checker.checkData(jsonData, nodeData);



function get_params(node){
	let copy = Object.keys(node.params).forEach(k => (!node.params[k] && node.params[k] !== undefined) && delete node.params[k]);
	return JSON.stringify(copy);
}

function post_request(node){
	return axios.post(server_url + node.Instance, {
		id : modelid,
		instance : exp_instance,
		params : get_params(node)
	  })
	  .then(function (response) {
		console.log(response.data);
		if(response.data.hasOwnProperty('plot_png')){
			const server = http.createServer(function(req, res) {
					  res.writeHead(200, {'Content-Type': 'text/html'});
					  res.write('<html><body><img src= ' + response.data.plot_png)
					  res.end('"></body></html>');
				  })
			server.listen(portCount);
			open('http://localhost:' + portCount + '/');
			portCount++;
			/*
			const close = (callback) => {
			  for (const socket of sockets) {
				socket.destroy();

				sockets.delete(socket);
			  }

			  server.close(callback);
			};
			*/
		}
	  })
	  .catch(function (error) {
		console.log(error);
	  });
}

function get_request(node){
	return axios.get(server_url + "/" + node.Instance)
	  .then(function (response) {
		console.log(response.data);
	  })
	  .catch(function (error) {
		console.log(error);
	  });
}

//runs the function associated to the node whose id is passed as a parameter
async function runNode(id){
	return await table[jsonData.nodes[id].Concept](jsonData.nodes[id]);
}

async function sequence(node){
	console.log("Running sequence node" + node.Instance);
	let child = node.firstChild;
	do{
		if(!(await runNode(child.Id))){
			return false;
		}
		child = child.Next;
	} while(child != null);
	return true;
}

async function priority(node){
	console.log("Running priority node" + node.Instance);
	let child = node.firstChild;
	do{
		if(await runNode(child.Id)){
			return true;
		}
		child = child.Next;
	} while(child != null);
	return false;
}

async function failer(node){
	console.log("Running Failer node " + node.Instance);
	return false;
}

async function succeeder(node){
	console.log("Running Succeeder node " + node.Instance);
	return true;
}

async function explanationMethod(node){
	console.log("Running Explanation Method " + node.Instance);
	await post_request(node);
	return true;
}

async function evaluationMethod(node){
	console.log("Running Evaluation Method" + node.Instance);
	//The return value should depend on the return value of the evaluation method
	return true;
}

async function repeater(node){
	console.log("Running Repeater " + node.Instance);
	for(var i = 0; i < node.properties.maxLoop; i++){
		if(! (await runNode(node.firstChild.Id))){
			return false;
		}
	}
	return true;
}

async function repeatUntilFailure(node){
	console.log("Running Repeat Until Failure " + node.Instance);
	while(await runNode(node.firstChild.Id));
	return true;
}

async function repeatUntilSuccess(node){
	console.log("Running Repeat Until Success " + node.Instance);
	while(! (await runNode(node.firstChild.Id)));
	return true;
}

async function inverter(node){
	console.log("Running Inverter " + node.Instance);
	return  ! (await runNode(node.firstChild.Id));
}

//table for BT nodes
table["Sequence"] = sequence;
table["Priority"] = priority;
table["Failer"] = failer;
table["Succeeder"] = succeeder;
table["Explanation Method"] = explanationMethod;
table["Evaluation Method"] = evaluationMethod;
table["Repeater"] = repeater;
table["RepeatUntilFailure"] = repeatUntilFailure;
table["RepeatUntilSuccess"] = repeatUntilSuccess;
table["Inverter"] = inverter;

run();

