#!/usr/bin/env python3

#
# Santiago Larrain
# slarrain@uchicago.edu
#

import boto3

ec2 = boto3.resource('ec2')

# http://rob.salmond.ca/filtering-instances-by-name-with-boto3/
instance = ec2.instances.filter(Filters=[{
    'Name': 'tag:Name',
    'Values': ['slarrain']
}])

sl = list(instance.all())[0]
iid = sl.id

print ('Instance ID: ', sl.id)
print ('Launched at ', sl.launch_time, 'in availability zone ', sl.placement['AvailabilityZone'], '\n')

check = sl.describe_attribute(Attribute='disableApiTermination')
if (not check['DisableApiTermination']['Value']):
    sl.modify_attribute(Attribute='disableApiTermination', Value='True')

if (not check['DisableApiTermination']['Value']):
    sl.modify_attribute(DisableApiTermination={'Value': True})

try:
    sl.terminate()
except Exception as e:
    print ('Instance deletion failed with error:')
    print (e)

# OUTPUT
'''

Instance ID:  i-f5fbf06f
Launched at  2016-04-03 23:48:45+00:00 in availability zone  us-east-1c

Instance deletion failed with error:
An error occurred (OperationNotPermitted) when calling the TerminateInstances
operation: The instance 'i-f5fbf06f' may not be terminated. Modify its
'disableApiTermination' instance attribute and try again.

'''
