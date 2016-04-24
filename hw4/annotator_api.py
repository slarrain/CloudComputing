#
#    Santiago Larrain
#    slarrain@uchicago.edu
#


from bottle import route, run, request, response, template
import subprocess
import uuid
import base64
import hmac
import sha
import botocore.session
import boto3
from datetime import timedelta, datetime, date
import urllib
import urllib2
import os

ann_jobs = {}

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

# http://bottlepy.org/docs/dev/tutorial.html#html-form-handling
# http://bottlepy.org/docs/dev/tutorial.html#query-variables
@route('/annotator')
def do_file():
    #Using UUID instead of ints
    job_id = str(uuid.uuid4())    #Generate a random uuid

    filename = request.query.key   #Gets the filename uploaded by the user
    bucket = request.query.bucket

    res_code = response.status_code    # Gets the HTTP status code
    ec = run_gas(filename, job_id, bucket)    #Runs the annotator

    # #Add UUID to the log file
    # change_name(filename, job_id)

    #JSON return value according to instructions
    rv = {'code': res_code,
        'data': {
            'job_id': job_id,
            'file_submitted': filename.split('-')[-1],
            'input_file': filename
            }
        }
    return rv

@route('/log/:jobid')
def do_file(jobid):
    # jobid = request.query.jobid    #Get the jobID inputted by the user
    res_code = response.status_code    # Gets the HTTP status code
    # log = ""    # Initializes the variable. Might not be necessary


    if ann_jobs[jobid].poll() == None:
        return 'Could not get the Log File. <br> Job is still running'

    results_file = 'https://s3.amazonaws.com/gas-results/slarrain/'+jobid+'.annot.vcf'
    log_file = 'https://s3.amazonaws.com/gas-results/slarrain/'+jobid+'.vcf.count.log'

    results = urllib2.urlopen(results_file).read()
    log = urllib2.urlopen(log_file).read()


    # #Reads the log
    # with open (filename, 'r') as f:
    #     log = f.read()

    #Return JSON according to instructions
    rv = {'code': res_code,
        'data': {
            'job_id': jobid,
            'log': log,
            'results':results
            }
        }
    return rv

def change_name(filename, job_id):
    '''
    Makes a copy of the log file with a new name that uses the UUID to make it persistent
    '''
    head, filename = os.path.split(filename)
    filepath = '/home/ubuntu/mpcs/anntools/mpcs_anntools/data/'+filename+'.count.log'
    new_filepath = '/home/ubuntu/mpcs/anntools/mpcs_anntools/data/'+job_id+'.log'
    ec = subprocess.call(['cp', filepath, new_filepath])

def run_gas(filename, job_id, bucket):
    '''
    This function runs the annotator given a filename.
    Doesn't crash if the filename does not exists. But doesn't tell the user either.
    '''
    url = 'https://s3.amazonaws.com/'+bucket+'/'+filename
    path = '/home/ubuntu/mpcs/anntools/mpcs_anntools/data/'

    # # http://stackoverflow.com/questions/8384737/python-extract-file-name-from-path-no-matter-what-the-os-path-format
    # head, tail = os.path.split(filename)

    filepath = path+job_id+'.vcf'

    # http://stackoverflow.com/questions/19602931/basic-http-file-downloading-and-saving-to-disk-in-python
    urllib.urlretrieve(url, filepath)   # Download the file from S3 bucket

    P = subprocess.Popen(['python', '/home/ubuntu/mpcs/anntools/mpcs_anntools/run.py', filepath])

    ann_jobs[job_id] = P

    # TODO
    # Delete uuuid.vcf files inside of data/

@route ('/check_running_jobs')
def check():
    '''
    Check for running annotation jobs.
    Returns the Job ID of the running ones
    '''
    rv = []
    for job_id in ann_jobs:
        if ann_jobs[job_id].poll() == None:
            rv.append (job_id)
    if rv:
        return rv
    else:
        return 'No annotation jobs running at the moment'

run(host='0.0.0.0', port=8888, debug=True, reloader=True)
