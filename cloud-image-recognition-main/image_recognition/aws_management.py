import os

import boto3

session = boto3.Session(profile_name="default")

s3 = session.client("s3")

bucket_name = "project-data-kaustubh"
object_key = "app-tier"

filename = "test_0.JPEG"

if not os.path.exists("images"):
    os.mkdir("images")


def check_s3_object_exists(bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True, "Object Available."
    except s3.exceptions.NoSuchKey:
        return False, "No such object."
    except s3.exceptions.NoSuchBucket:
        return False, "No such bucket."
    except Exception as e:
        return False, e


status, statement = check_s3_object_exists(
    "project-data-kaustubh",
    "app-tier/data/imagenet-100-updated/imagenet-100/test_0.JPEG",
)

if status:
    s3.download_file(
        "project-data-kaustubh",
        "app-tier/data/imagenet-100-updated/imagenet-100/test_0.JPEG",
        os.path.join("images", filename),
    )
