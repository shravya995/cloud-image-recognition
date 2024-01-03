def create_s3_bucket(s3_client, bucket_name, region="us-east-1"):
    # Check if the bucket already exists
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"The bucket '{bucket_name}' already exists.")
    except Exception as e:
        # Bucket doesn't exist, so create it
        if e.response["Error"]["Code"] == "404":  # type: ignore
            try:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                )
                print(
                    f"Bucket '{bucket_name}' created successfully in region '{region}'."
                )
            except Exception as create_error:
                print(
                    f"Error creating bucket '{bucket_name}': {str(create_error)}"
                )
        else:
            print(f"Error checking bucket '{bucket_name}': {str(e)}")
