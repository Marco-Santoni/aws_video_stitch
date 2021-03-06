import boto3
import os
import yaml
from datetime import datetime

CONFIG_FILE = 'config.yaml'
with open(CONFIG_FILE, 'r') as stream:
    config = yaml.load(stream)

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
et_client = boto3.client('elastictranscoder', 'us-west-2')

def copy_all_contents(s3_client, from_bucket, to_bucket):
    print('copying files from {} to {}'.format(from_bucket, to_bucket))
    for content in s3_client.list_objects(Bucket=from_bucket)['Contents']:
        file_key = content['Key']
        copy_source = {'Bucket': from_bucket, 'Key': file_key}
        s3_client.copy(copy_source, to_bucket, file_key)

UPLOAD_FIRST = True

if UPLOAD_FIRST:
    # empty the bucket first
    print('emptying {} bucket'.format(config['INPUT_BUCKET']))
    s3_resource.Bucket(config['INPUT_BUCKET']).objects.all().delete()
    # Upload raw videos. Overwrites if existing
    for videofile in [\
        v for v in os.listdir(config['LOCAL_INPUT_DIR']) if v[-4:] == config['INPUT_FILE_FMT']\
    ]:
        print('uploading {}'.format(videofile))
        s3_client.upload_file(
            config['LOCAL_INPUT_DIR'] + videofile,
            config['INPUT_BUCKET'],
            videofile
        )

response = s3_client.list_objects(
    Bucket=config['INPUT_BUCKET']
)
keys = [{"Key": c["Key"]} for c in  response["Contents"]]

# Video need all same format
OUTPUT_FILE = '{}.mp4'.format(int(datetime.now().timestamp()))

response = et_client.create_job(
  PipelineId=config['PIPELINE_ID'],
  Inputs=keys,
  Output={'Key': OUTPUT_FILE, 'PresetId': config['PRESET_ID']}
)

       # wait for elastictranscoder job to complete
et_job_id = response['Job']['Id']
waiter = et_client.get_waiter('job_complete')
waiter.wait(
    Id=et_job_id,
    WaiterConfig={
        'Delay': 2,
        'MaxAttempts': 120
    }
)

# copy stitched video to permanent storage
copy_all_contents(
    s3_client,
    from_bucket=config['OUTPUT_BUCKET'],
    to_bucket=config['STITCHED_VIDEO_BUCKET']
)
s3_resource.Bucket(config['OUTPUT_BUCKET']).objects.all().delete()

# copy raw videos to permanent storage
copy_all_contents(
    s3_client,
    from_bucket=config['INPUT_BUCKET'],
    to_bucket=config['RAW_VIDEO_BUCKET']
)
s3_resource.Bucket(config['INPUT_BUCKET']).objects.all().delete()
