import boto3
import os
basedir = os.path.abspath(os.path.dirname(__file__))

def _get_s3_resource():
    S3_KEY= os.environ.get("s3_accessKey")
    S3_SECRET=os.environ.get("s3_accessSecret")
    if S3_KEY and S3_SECRET:
        return boto3.resource(
            's3',
            aws_secret_access_key=S3_SECRET,
            aws_access_key_id=S3_KEY
        )
    else:
        return boto3.resource('s3')

def get_bucket():
    S3_BUCKET = os.environ.get("s3_bucketName")
    s3_resource = _get_s3_resource()
    return s3_resource.Bucket(S3_BUCKET)
