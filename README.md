# Stitch videos in AWS

This Python script automates the stitching of multiple videos in a single one. The script will

- upload all the videos from a local folder to a AWS S3 bucket
- launch an Elastic Transcoder job that stitches the videos together
- move the input videos and the output video to other target S3 buckets
- delete the videos in the input/output buckets

## Setup and Run

You need to create an Elastic Transcoder pipeline prior to launching the script. The pipeline needs to be set with the same S3 buckets of the ones used by the script. The pipeline id and the S3 bucket names can be set in a `config.yaml` file. The structure of the file is described in `example_config.yaml`.

To install the python dependencies and run the script:

```bash
pip install -r requirements.txt
python main.py
```
