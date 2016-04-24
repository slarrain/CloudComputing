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
            <br><br>
            <a href="/upload"> UPLOAD (HW3) </a> <br>
            <a href="/input-files"> Input files (HW3) </a>
            </html>
            '''

# For exercise 2.a
# http://bottlepy.org/docs/dev/tutorial.html#html-form-handling
@route('/filein', method='POST')
def do_file():
    #Using UUID instead of ints
    job_id = str(uuid.uuid4())    #Generate a random uuid

    filename = request.forms.get('filename')    #Gets the filename inputted by the user
    res_code = response.status_code    # Gets the HTTP status code
    ec = run_gas(filename)    #Runs the annotator

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
    jobid = request.forms.get('jobid')    #Get the jobID inputted by the user
    res_code = response.status_code    # Gets the HTTP status code
    log = ""    # Initializes the variable. Might not be necessary

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


@route('/upload', method='GET')
def upload_file_to_s3():
    '''
    Help from:
        https://forums.aws.amazon.com/thread.jspa?messageID=314467
        http://stackoverflow.com/questions/36287720/boto3-get-credentials-dynamically
        http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingHTTPPOST.html and nexts
    '''
    # Define S3 policy document

    delta = timedelta(days=10) # 10 days of expiration
    today = datetime.today()
    exp = (today+delta).isoformat()
    # I'm getting a weird error: Invalid Policy: Invalid 'expiration' value: '2016-04-28T23:31:36.798044'
    # Using hardcoded date
    policy_doc = { "expiration": "2017-12-01T12:00:00.000Z",
                      "conditions": [
                        {"acl": "public-read" },
                        {"bucket": "gas-inputs"},
                         ["starts-with", "$key", "slarrain/"],
                         {"success_action_redirect": "https://s3.amazonaws.com/gas-inputs/slarrain/upload_succesful.html"  }
                        ]
                    }

    # https://s3.amazonaws.com/gas-inputs/slarrain/upload_succesful.html
    # Encode and sign policy document
    session = botocore.session.get_session()
    aws_access_key = session.get_credentials().access_key
    aws_secret_key = session.get_credentials().secret_key
    policy_doc = "".join(str(policy_doc).split())    #Remove all whitespace

    # Encode the policy in base64
    policy_encoded = base64.b64encode(policy_doc)

    signature = base64.b64encode(hmac.new(str(aws_secret_key), str(policy_encoded), sha).digest())
    # This was helpful: http://stackoverflow.com/questions/20849805/python-hmac-typeerror-character-mapping-must-return-integer-none-or-unicode

    # Render the upload form
    return template("upload.tpl", bucket_name="gas-inputs", aws_key=str(aws_access_key), aws_username="slarrain", policy_encod=str(policy_encoded), signat=str(signature))


@route('/input-files', method='GET')
def get_s3_content():
    # http://stackoverflow.com/questions/30249069/listing-contents-of-a-bucket-with-boto3

    s3 = boto3.client('s3')
    res_code = response.status_code    # Gets the HTTP status code
    file_list = []
    for key in s3.list_objects(Bucket='gas-inputs', Prefix='slarrain/')['Contents']:
        file_list.append(key['Key'])

    #JSON return value according to instructions
    rv = {'code': res_code,
        'data': {
            'files': file_list
            }
        }
    return rv

@route("/redirect")
def redir():
    # Didn't use it
    return '''
                <html>
                <h1>
                  The Upload was Succesful!
                </h1>
                <html>
            '''

run(host='0.0.0.0', port=8888, debug=True, reloader=True)
