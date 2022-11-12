from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for
from flask_httpauth import HTTPBasicAuth


app = Flask(__name__)


#Authentication system
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
	if username == 'Antoh':
		return 'kip'

@auth.error_handler
def unauthorized():
	return make_response(jsonify({'error':'Unauthorized Access'}), 403)

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


#api to get specific task by id
#(curl command )curl -i http://localhost:5000/todo/api/v1/tasks/2
@app.route('/todo/api/v1/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
    task = []
    for tk in tasks:
        if tk['id']==task_id:
            task.append(tk)        
    if len(task)==0:
        abort(404)
    return jsonify({'task': make_task_public(task[0])})



#api endpoint to create a task
@app.route('/todo/api/v1/tasks', methods=['POST'])
@auth.login_required
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
    return jsonify({'task':make_task_public(task)}), 201 #status code for created


#api endpoint to update an existing task or create new one
@app.route('/todo/api/v1/tasks/<int:task_id>', methods=['PUT'])
#(curl test command)curl -i -H "Content-Type: application/json" -X PUT -d "{\"Done\":true, \"title\":\"Uhuru si mubaya\"}" http://localhost:5000/todo/api/v1/tasks/1
@auth.login_required
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
	return jsonify({'task':make_task_public(task[0])}), 202	


#api endpoint to delete a task by id
@app.route('/todo/api/v1/tasks/<int:task_id>', methods=['DELETE'])
#(curl test command) curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/todo/api/v1/tasks/2
@auth.login_required
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
#(curl command )curl -i http://localhost:5000/todo/api/v1/tasks
@auth.login_required
def get_tasks():
	public_tasks = []
	for task in tasks:
		new_t = make_task_public(task)
		public_tasks.append(new_t)
	return jsonify({'tasks':public_tasks})

#helper function to generate public version(shows URI that controls the task) of task to send to client
def make_task_public(task):
	new_task = {}
	for field in task:
		if field=='id':
			new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
		else:
			new_task[field] = task[field]
	return new_task


#entry point to our script
if __name__ == '__main__':
    app.run(debug=True)
