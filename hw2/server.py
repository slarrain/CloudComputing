#
#	Santiago Larrain
#	slarrain@uchicago.edu
#


from bottle import route, run, request, response, subprocess
import uuid

@route('/')
def hello():
	return '''
			<html>
			<form action="/filein" method="post">
			    Filename: <input name="filename" type="text" />
			    <input value="OK" type="submit" />
			</form>
			<form action="/fileout" method="post">
			    Job ID: <input name="jobid" type="text" />
			    <input value="OK" type="submit" />
			</form>
			</html>
			'''

# For exercise 2.a
# http://bottlepy.org/docs/dev/tutorial.html#html-form-handling
@route('/filein', method='POST')
def do_file():
	#Using UUID instead of ints
	job_id = str(uuid.uuid4())	#Generate a random uuid

	filename = request.forms.get('filename')	#Gets the filename inputted by the user
	res_code = response.status_code	# Gets the HTTP status code
	ec = run_gas(filename)	#Runs the annotator

	#Add UUID to the log file
	change_name(filename, job_id)

	#JSON return value according to instructions
	rv = {'code': res_code, 
		'data': {
			'job_id': job_id,
			'input_file': filename
			}
		}
	return rv
	
#For exercise 2.b
@route('/fileout', method='POST')	
def do_file():
	jobid = request.forms.get('jobid')	#Get the jobID inputted by the user
	res_code = response.status_code	# Gets the HTTP status code
	log = ""	# Initializes the variable. Might not be necessary

	filename = '/home/ubuntu/mpcs/anntools/mpcs_anntools/data/'+jobid+'.log'

	#Reads the log
	with open (filename, 'r') as f:
		log = f.read()

	#Return JSON according to instructions
	rv = {'code': res_code, 
		'data': {
			'job_id': jobid,
			'log': log
			}
		}
	return rv

def change_name(filename, job_id):
	'''
	Makes a copy of the log file with a new name that uses the UUID to make it persistent
	'''
	filepath = '/home/ubuntu/mpcs/anntools/mpcs_anntools/data/'+filename+'.count.log'
	new_filepath = '/home/ubuntu/mpcs/anntools/mpcs_anntools/data/'+job_id+'.log'
	ec = subprocess.call(['cp', filepath, new_filepath])

def run_gas(filename):
	'''
	This function runs the annotator given a filename.
	Doesn't crash if the filename does not exists. But doesn't tell the user either.
	'''
	filepath = '/home/ubuntu/mpcs/anntools/mpcs_anntools/data/'+filename
	try:
		exitcode = subprocess.call(['python', '/home/ubuntu/mpcs/anntools/mpcs_anntools/run.py', filepath])
		return exitcode
	except Exception as e:
		return exitcode

run(host='0.0.0.0', port=8888, debug=True)
