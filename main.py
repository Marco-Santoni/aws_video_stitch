import boto3
import os
import yaml
from datetime import datetime

CONFIG_FILE = 'config.yaml'
with open(CONFIG_FILE, 'r') as stream:
    config = yaml.load(stream)

s3_client = boto3.client('s3')
et_client = boto3.client('elastictranscoder', 'us-west-2')

# Video need all same format
OUTPUT_FILE = '{}.mp4'.format(int(datetime.now().timestamp()))
UPLOAD_FIRST = False

if UPLOAD_FIRST:
    # Overwrites if existing. Make sure there are not undesired files
    for videofile in [\
        v for v in os.listdir(config['LOCAL_INPUT_DIR']) if v[-4:] == '.mp4'\
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

et_client.create_job(
  PipelineId=config['PIPELINE_ID'],
  Inputs=keys,
  Output={'Key': OUTPUT_FILE, 'PresetId': config['PRESET_ID']}
)
       
