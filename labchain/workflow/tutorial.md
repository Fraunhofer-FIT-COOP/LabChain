# Labchain Workflow Management System Tutorial
In order to use the system, first do the following:
* Run the node. `-v` and `-vv` set the log level to INFO or DEBUG. `-d` to start a new blockchain from scratch.

```sh
$ python3 node.py
```

* Run the client

```sh
$ python3 client.py --doc
```
Depending on the value chosen on client, the following functionalities can be achieved:

### Creating a new workflow transaction:
>In order to create a workflow, first a template for the desired workflow should be created under the `resources` folder. A workflow template consists of a `document` which are the values that will be modified throughout the workflow, `processes` that define the workflow itself, `permissions` which define which entities are allowed to modify which values, `splits` which define the type of merge for the *receiver* address, and `in_charge` which should be the first person to start the workflow. In the system, the created workflow transaction is sent to the creator, therefore this entity should be the creator itself.

 Once the template is ready, in the client choose `1- Create workflow transaction` and choose the name of the template that is created. Choose a sender account and choose the accounts that will be used for the other entities in the workflow definition. It is not allowed to use the same key for multiple entities. Use
 ```sh
$ python3 client.py
```
and choose `1- Manage Wallet` to manage your wallet in case the number of keys required are not defined yet. After choosing the entity addresses, the client will show the the whole workflow with the given addresses. Finally, enter the workflow id (which should be a number) and the workflow transaction is created and its hash is displayed.

### Sending a transaction for a defined workflow:

In order to send a transaction, first choose `2- Send transaction` and then choose the sender address that will be used to send the transaction. This will display all the workflow stages that are not participated yet with the document values that are sent. Due to mining time, it might take some time to see all the tasks available. Choose the workflow id that is desired. The possible receivers for the task will be listed according to the initial workflow definition that is made, pick the receiver. The variable inside the document that is possible for the given sender address will be displayed. Put the value for the variable and press enter. The transaction is created and the related info is displayed.

### Displaying the status of the current workflows:
In order to display the current status of each workflow that is created, first choose `3- Show workflow status` and then choose the address that the related workflows will be displayed. The workflow id and the template name is displayed among the current status of the workflow. If the workflow is completed, it will only show "Completed", whileas if the workflow is "In Progress", the next person that needs to modify a variable in the document is displayed.

### Displaying the details of a document inside a workflow :
In order to display the document details of a workflow, first choose `4- Show workflow details` and choose the address that the desired workflow is created from. Then choose a workflow id among all the workflow ids that are related to desired address. The states of the variables inside the document of the workflow will be displayed.