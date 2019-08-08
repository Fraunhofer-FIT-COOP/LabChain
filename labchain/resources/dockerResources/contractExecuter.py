from flask import Flask, abort, request
import json
import pickle
import codecs
import importlib
import inspect
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
	return json.dumps("Container is running")


@app.route('/createContract', methods=['POST'])
def createContract():
	"""JSON FORMAT FOR CREATING A CONTRACT
	{
	"contractCode": "Encoded string in base64 containing the contract's code",
    "arguments": 
		{ 
			"Arg1Name": "Arg1", 
			"Arg2Name": "Arg2", 
			"Arg3Name": Arg3
			...
    	},
	"contract_file_name": "my_contract_name.py"
	}
	Note: the "arguments" here are the arguments for the constructor.
	May also be left empty if the constructor doesn't need any.
	"""
	if not request.json:
		abort(400)
	
	# Fetch received data
	data_dict = request.json
	contract_file_name = data_dict['contract_file_name']
	code = data_dict['code']
	arguments = data_dict['arguments']

	# Fetch arguments needed for the constructor
	args = tuple(arguments.values())

	#Try to create the contract .py file. Return an error if not possible
	createContractErrorMessage = createContractHelper(code, contract_file_name)
	if createContractErrorMessage != None:
		return createContractErrorMessage

	#Import module dynamically
	module = importlib.import_module(contract_file_name[:-3])

	mainClass = inspect.getmembers(module)[0][0]
	mainClassName = str(mainClass)

	# Check if the arguments the user provided are correct, if not return an error
	falseArgumentsErrorMessage = falseArgumentsInMethod(module, mainClassName, args)
	if falseArgumentsErrorMessage != None:
		return falseArgumentsErrorMessage

	# Create a contracts instance with the fetched arguments and encode it to send back
	contractInstance = getattr(module, mainClass)(*args)
	encodedInstance = codecs.encode(pickle.dumps(contractInstance), "base64").decode()

	# Prepare response
	try:
		updatedState = getattr(contractInstance, "to_dict")()
	except:
		updatedState = "Contract has no method 'to_dict' available."
	response = {
		"success": True,
		"newState": updatedState,
		"encodedNewState": encodedInstance
	}
	return json.dumps(response, indent=4, sort_keys=False)


@app.route('/callMethod', methods=['POST'])
def callMethod():
	"""JSON FORMAT FOR CALLING A METHOD
{
	"methods": 
		[
			{
				"methodName": method_1_name,
				"arguments": 
				{
					"method1Arg1Name": method_1_Arg1
					"method1Arg2Name": method_1_Arg2
					...
				}
			},
			{
				"methodName": method_2_name,
				"arguments": 
				{
					"method2Arg1Name": method_2_Arg1
					"method2Arg2Name": method_2_Arg2
					...
				}
			},
			...
		],
	"contract_file_name": "my_contract_name.py"
}
	Note: the "arguments" here are the arguments for each method.
	May also be left empty if the method doesn't need any.
	"""
	if not request.json:
		abort(400)
	
	# Fetch received data
	data_dict = request.json
	state = data_dict['state']
	methods = data_dict['methods']
	contract_file_name = data_dict['contract_file_name']

	try:
		#Import module dynamically
		module = importlib.import_module(contract_file_name[:-3])
	except:
		errorMessage = "Contract file could not be found. (callMethod function)"
		return jsonError(errorMessage)

	# Create a contracts instance with the fetched state
	try:
		contractInstance = pickle.loads(codecs.decode(state.encode(), "base64"))
	except:
		errorMessage = "The state provided could not be decoded. String may be corrupted. (callMethod function)"
		return jsonError(errorMessage)

	# Fetch all methods to call and their arguments and call them
	for method in methods:
		methodName = method['methodName']

		# Check if method exists, if not, return error
		if methodName not in dir(contractInstance):
			errorMessage = "Contract does not contain any " + methodName + " method."
			return jsonError(errorMessage) 

		arguments = method['arguments']
		args = tuple(arguments.values())
		print(args)

		# Check if the arguments the user provided are correct, if not return an error
		falseArgumentsErrorMessage = falseArgumentsInMethod(contractInstance, methodName, args)
		if falseArgumentsErrorMessage != None:
			return falseArgumentsErrorMessage

		try:
			getattr(contractInstance, methodName)(*args)
		except:
			errorMessage = "Contract's method " + methodName + " does not take argument '" + str(arguments) + "'."
			return jsonError(errorMessage)
			
	# Encode updated the updated contract's state to send back
	encodedInstance = codecs.encode(pickle.dumps(contractInstance), "base64").decode()
	
	# Prepare response
	try:
		updatedState = getattr(contractInstance, "to_dict")()
	except:
		updatedState = "Contract does not contain any 'to_dict' method."
	response = {
		"success": True,
		"updatedState": updatedState,
		"encodedUpdatedState": encodedInstance
	}
	return json.dumps(response, indent=4, sort_keys=False)


@app.route('/getState', methods=['POST'])
def getState():
	"""JSON FORMAT FOR GETTING A CONTRAT'S STATE
	{
	"state": "Encoded string in base64 containing the contract's state"
	}
	"""
	if not request.json:
		abort(400)
	
	# Fetch received data
	data_dict = request.json
	state = data_dict['state']

	# Create a contracts instance with the fetched state
	try:
		contractInstance = pickle.loads(codecs.decode(state.encode(), "base64"))
	except:
		errorMessage = "The state provided could not be decoded. String may be corrupted. (getState function)"
		return jsonError(errorMessage)
		
	# Prepare response
	try:
		updatedState = getattr(contractInstance, "to_dict")()
	except:
		updatedState = "Contract does not contain any 'to_dict' method."
	response = {
		"success": True,
		"state": updatedState
	}
	return json.dumps(response, indent=4, sort_keys=False)


@app.route('/getMethods', methods=['POST'])
def getMethods():
	"""JSON FORMAT FOR GETTING A LIST OF A CONTRACT'S METHODS
	{
	"state": "Encoded string in base64 containing the contract's state"
	}
	"""
	if not request.json:
		abort(400)
	
	# Fetch received data
	data_dict = request.json
	state = data_dict['state']

	# Create a contracts instance with the fetched state
	try:
		contractInstance = pickle.loads(codecs.decode(state.encode(), "base64"))
	except:
		errorMessage = "The state provided could not be decoded. String may be corrupted. (getMethods Function)"
		return jsonError(errorMessage)

	object_attributes = [f for f in dir(contractInstance) 
						if (f[0] != '_' and not(callable(f)))]

	paramDict = {}
	for attributeName in object_attributes:
		try:
			method = getattr(contractInstance, attributeName)
			methodParams = inspect.signature(method).parameters.items()
			
			paramList = []
			for key, value in methodParams:
				print(key)
				print(value)
				paramList.append(str(value))
			paramDict[attributeName] = paramList
		except:
			pass
	
	response = {
				"success": True,
				"methods": paramDict
			}
	return json.dumps(response, indent=4, sort_keys=False)


@app.route('/getAttributes', methods=['POST'])
def getAttributes():
	"""JSON FORMAT FOR GETTING A CONTRAT'S STATE
	{
	"state": "Encoded string in base64 containing the contract's state",
	"methodName": "String of the method's name"
	}
	"""
	if not request.json:
		abort(400)
	
	# Fetch received data
	data_dict = request.json
	state = data_dict['state']
	methodName = data_dict['methodName']

	# Create a contracts instance with the fetched state
	try:
		contractInstance = pickle.loads(codecs.decode(state.encode(), "base64"))
	except:
		errorMessage = "The state provided could not be decoded. String may be corrupted. (getAttributes function)"
		return jsonError(errorMessage)

	# Check if method exists, if not, return error
	if methodName not in dir(contractInstance):
		errorMessage = "Contract does not contain any " + methodName + " method."
		return jsonError(errorMessage)

	method = getattr(contractInstance, str(methodName))
	methodParams = inspect.signature(method).parameters.items()
	
	paramDict = {}
	for key, value in methodParams:
		paramDict[str(key)] = str(value).split(":")[1]

	response = {
				"success": True,
				"parameters": paramDict
			}
	return json.dumps(response, indent=4, sort_keys=False)

def createContractHelper(code, contract_file_name):
	noError = None
	

	# Decode the string 'code' provided, write it into a .py file 
	# and import it dynamically
	try:
		codeString = pickle.loads(codecs.decode(code.encode(), "base64"))
		with open(contract_file_name, 'w') as file:
			file.write(str(pickle.loads(codeString)))
	except:
		errorMessage = "The code provided could not be decoded. String may be corrupted."
		return jsonError(errorMessage)
	
	return noError

def falseArgumentsInMethod(contractInstance, methodName, arguments):
	noError = None

	method = getattr(contractInstance, methodName)
	methodParams = inspect.signature(method).parameters.items()

	# Check if number of arguments is correct
	if len(methodParams) != len(arguments):
		if len(methodParams) < len(arguments):
			errorMessage = ("Too many arguments provided to " + 
							str(method).replace("<","'").replace(">","'") + 
							". This method takes " + str(len(methodParams)) + 
							" argument(s).")
			return jsonError(errorMessage)
		else:
			errorMessage = ("Not enough arguments provided to " + 
							str(method).replace("<","'").replace(">","'") + 
							". This method takes " + str(len(methodParams)) + 
							" argument(s).")
			return jsonError(errorMessage)
		
	# Check if the arguments the user provided are of the correct type
	for index, expectedArg in enumerate(inspect.signature(method).parameters.values()):
		if(type(arguments[index]) != expectedArg.annotation):
			errorMessage = ("Argument " + str(expectedArg).split(":")[0] + 
							" received a " + str(type(arguments[index])).split("'")[1] + 
							" type object. A" + str(expectedArg).split(":")[1] + 
							" type is expected.")
			return jsonError(errorMessage)
	
	return noError


def jsonError(errorMessage: str):
	response = {
		"success": False,
		"error": errorMessage
	}
	return json.dumps(response, indent=4, sort_keys=False)


if __name__ == '__main__':
	app.run("0.0.0.0", port=80, debug=True)