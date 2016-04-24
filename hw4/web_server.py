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
            <a href="/upload"> UPLOAD (HW3) </a> <br>
            <a href="/input-files"> Input files (HW3) </a>
            </html>
            '''

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
                         {"success_action_redirect": "http://54.174.243.246:8888/annotator"  }
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

    # UUID for the filename
    filename_id = str(uuid.uuid4())

    # Render the upload form
    return template("upload.tpl", bucket_name="gas-inputs", filename_id=filename_id, aws_key=str(aws_access_key), aws_username="slarrain", policy_encod=str(policy_encoded), signat=str(signature))


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
