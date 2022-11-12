from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request


app = Flask(__name__)


#dummy database
tasks = [
    {'id':1,
     'title':u'to figure out mpesa intergration',
     'Description':u'Work with the existing module and tweak it',
     'Done':False
     },
    {'id':2,
     'title':u'Build jemos website',
     'Description':u'use wordpress for quick delivery',
     'Done':False
     }
    ]

@app.route('/todo/api/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = []
    for tk in tasks:
        if tk['id']==task_id:
            task.append(tk)        
    if len(task)==0:
        abort(404)
    return jsonify({'task': task[0]})

#api endpoint to create a task
@app.route('/todo/api/v1/tasks', methods=['POST'])
def create_task():
    #(curl command to test) curl -i -H "Content-Type: application/json" -X POST -d "{\"title\":\"Read a book\"}" http://localhost:5000/todo/api/v1/tasks
    
    #request.json will have  the request data only if it came marked as JSON 
    if not request.json or not 'title' in request.json:
        abort(400) #bad request status_code
    task = {
        'id':tasks[-1]['id']+1, #easy way to guarantee unique ids in our simple db
        'title':request.json['title'],
        'Description':request.json.get('Description',""), #tolerate missing desc
        'Done':False
        }
    tasks.append(task)
    return jsonify({'task':task}), 201 #status code for created


#api endpoint to update an existing task or create new one
@app.route('/todo/api/v1/tasks/<int:task_id>', methods=['PUT'])
#(curl test command)curl -i -H "Content-Type: application/json" -X PUT -d "{\"Done\":true, \"title\":\"Uhuru si mubaya\"}" http://localhost:5000/todo/api/v1/tasks/1
def update_task(task_id):
	task = []
	for tk in tasks:
		if tk['id']==task_id:
			task.append(tk)
	if len(task)==0:
	    abort(404)
	if not request.json:
	    abort(400)
	if 'title' in request.json and type(request.json['title']) != str:
		abort(400)
	if 'Description' in request.json and type(request.json['Description']) is not str:
		abort(400)
	if 'Done' in request.json and type(request.json['Done']) is not bool:
		abort(400)
	task[0]['title'] = request.json.get('title', task[0]['title'])
	task[0]['Description'] = request.json.get('Description', task[0]['Description'])
	task[0]['Done'] = request.json.get('Done', task[0]['Done'])
	return jsonify({'task':task[0]}), 202	


#api endpoint to delete a task by id
@app.route('/todo/api/v1/tasks/<int:task_id>', methods=['DELETE'])
#(curl test command) curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/todo/api/v1/tasks/2
def delete_task(task_id):
	task = []
	for tk in tasks:
		if tk['id']==task_id:
			task.append(tk)
	if len(task)==0:
		abort(404)
	tasks.remove(task[0])
	return jsonify({'Result':'Deletion Successful'})

#to ensure the error returned is not html data but json data
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error':'Not found'}),404)

#api endpoint to get tasks avilable in db
@app.route('/todo/api/v1/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks':tasks})


#entry point to our script
if __name__ == '__main__':
    app.run(debug=True)
