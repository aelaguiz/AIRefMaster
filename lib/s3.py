import boto3
import json

import random
import string

def load_s3_config():
    print("Loading S3 config...")
    with open('config.json', 'r') as f:
        config = json.load(f)
    print("S3 config loaded.", config['s3'])
    return config['s3']

def upload_to_s3(content, mime_type, file_name):
    print("Uploading to S3...")
    s3_config = load_s3_config()
    s3 = boto3.client('s3',
                      aws_access_key_id=s3_config['aws_access_key_id'],
                      aws_secret_access_key=s3_config['aws_secret_access_key'],
                      region_name=s3_config['region'])
    
    s3.put_object(Body=content, Bucket=s3_config['bucket_name'], Key=file_name, ContentType=mime_type)
    print("Upload successful.")

    public_url = f"https://{s3_config['bucket_name']}.s3.{s3_config['region']}.amazonaws.com/{file_name}"
    return public_url

def generate_random_text(size=1000):
    """Generate a random string of letters and digits."""
    print("Generating random text...")
    letters_and_digits = string.ascii_letters + string.digits
    random_text = ''.join(random.choice(letters_and_digits) for i in range(size))
    print("Random text generated.")
    return random_text

def test_s3():
    print("Testing S3 upload...")
    s3_config = load_s3_config()
    random_text = generate_random_text()
    file_name = "test_random.txt"
    
    upload_to_s3(random_text.encode(), "text/plain", file_name)
    print(f"File {file_name} uploaded to S3.")

    # Assuming the bucket is publicly accessible
    public_url = f"https://{s3_config['bucket_name']}.s3.{s3_config['region']}.amazonaws.com/{file_name}"
    print(f"Test file should be accessible at: {public_url}")
