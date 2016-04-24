# Copyright (C) 2011-2016 Vas Vasiliadis
# University of Chicago
##
__author__ = 'Vas Vasiliadis <vas@uchicago.edu>'

import sys
import time
import driver
import boto3
import glob
import os


# A rudimentary timer for coarse-grained profiling
class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print "Elapsed time: %f ms" % self.msecs

def upload_to_s3():

    # https://docs.python.org/2/library/glob.html
    path = '/home/ubuntu/mpcs/anntools/mpcs_anntools/data/'
    annot = path+'*.annot.vcf'
    log = path+'*.count.log'
    l1 = glob.glob(annot)
    l2 = glob.glob(log)
    files = l1+l2 #List of files to upload

    # Upload to S3
    # https://boto3.readthedocs.org/en/latest/guide/migrations3.html#storing-data
    s3 = boto3.resource('s3')

    for filename in files:
        head, namefile = os.path.split(filename)
        #print head, namefile
        #Uploads the file
        print 'Uploading file to S3...'
        s3.Object('gas-results', 'slarrain/'+namefile).put(ACL='public-read', Body=open(filename, 'r'))
        print 'Deleting file...'
        os.remove(filename) # Deletes the file

if __name__ == '__main__':
    # Call the AnnTools pipeline
    if len(sys.argv) > 1:
        input_file_name = sys.argv[1]
        with Timer() as t:
            driver.run(input_file_name, 'vcf')
        print "Total runtime: %s seconds" % t.secs
        upload_to_s3()
        print 'Files deleted!'
    else:
        print 'A valid .vcf file must be provided as input to this program.'
