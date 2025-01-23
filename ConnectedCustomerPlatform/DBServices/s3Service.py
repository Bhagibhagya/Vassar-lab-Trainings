import logging
import boto3
import os
import uuid
from urllib.parse import urlparse
from datetime import datetime
from botocore.exceptions import ClientError

from django.conf import settings


class S3Manager:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        self.s3 = boto3.client('s3',
                               aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key,
                               region_name=region_name)

    def upload_attachments_to_s3(self, file_paths,bucket_name="connected-customer", project="connected_customer", customer="GP", customer_client="vassar"):
        """
        Uploads multiple files to an S3 bucket with a hierarchical structure.

        :param bucket_name: Name of the S3 bucket.
        :param file_paths: List of file paths.
        :param project: Name of the project.
        :param customer: Name of the customer.
        :param customer_client: Name of the customer client.
        :param year: Year.
        :param month: Month.
        :return: List of URLs of the uploaded objects if successful, else None.
        """
        uploaded_urls = []
        year = datetime.now().year
        month = datetime.now().strftime("%B")
        try:
            # Validate bucket name
            self.s3.head_bucket(Bucket=bucket_name)  # This will raise an exception if the bucket doesn't exist or is not accessible

            for file_path in file_paths:
                # Check if 'file_path' is a valid file
                if not os.path.isfile(file_path):
                    print(f"Invalid File Path: {file_path}")
                    continue

                # Extract file name from the file path
                file_name = os.path.basename(file_path)

                # Construct the object key based on the hierarchical structure
                object_key = f"{project}/{customer}/{customer_client}/{year}/{month}/Attachments/{file_name}"

                # Upload file to S3
                self.s3.upload_file(file_path, bucket_name, object_key)

                file_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
                print(f"File '{file_name}' uploaded to '{bucket_name}' with object name '{object_key}' successfully.")
                print(f"Object URL: {file_url}")
                uploaded_urls.append(file_url)

                # Delete the file from the local system
                os.remove(file_path)
                print(f"File '{file_path}' deleted from local system.")

            return uploaded_urls
        except Exception as e:
            print(f"Error uploading files: {e}")
            return None



    def upload_email_body_to_s3(self, email_body, bucket_name ="connected-customer",  project="connected_customer", customer="GP", customer_client="vassar"):
        """
        Uploads email body content to an S3 bucket with a hierarchical structure.

        :param bucket_name: Name of the S3 bucket.
        :param email_body: Email body content.
        :param project: Name of the project.
        :param customer: Name of the customer.
        :param customer_client: Name of the customer client.
        :param year: Year.
        :param month: Month.
        :return: URL of the uploaded object if successful, else None.
        """
        try:
            year = datetime.now().year
            month = datetime.now().strftime("%B")
            # Validate bucket name
            self.s3.head_bucket(Bucket=bucket_name)  # This will raise an exception if the bucket doesn't exist or is not accessible

            # Construct a unique object name based on UUID
            object_name = str(uuid.uuid4())

            # Construct the object key based on the hierarchical structure
            object_key = f"{project}/{customer}/{customer_client}/{year}/{month}/Email_body/{object_name}.txt"

            # Upload email body content to S3
            self.s3.put_object(Body=email_body.encode('utf-8'), Bucket=bucket_name, Key=object_key)

            file_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
            print(f"Email body uploaded to '{bucket_name}' with object name '{object_key}' successfully.")
            print(f"Object URL: {file_url}")
            return file_url
        except Exception as e:
            print(f"Error uploading email body: {e}")
            return None

    def update_email_body_to_s3(self, email_body, previous_body_url, bucket_name="connected-customer"):
        """
        Uploads email body content to an S3 bucket with a hierarchical structure, replacing the previous body content.

        :param bucket_name: Name of the S3 bucket.
        :param email_body: Email body content.
        :param previous_body_url: URL of the previous email body object.
        :return: URL of the uploaded object if successful, else None.
        """
        try:
            # Extract object key from previous body URL
            object_key = previous_body_url.split(bucket_name + ".s3.amazonaws.com/")[1]

            # Upload new email body content to S3, replacing the previous content
            self.s3.put_object(Body=email_body.encode('utf-8'), Bucket=bucket_name, Key=object_key)

            new_file_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
            print(f"Email body replaced at '{previous_body_url}' with new content uploaded to '{bucket_name}' with object name '{object_key}' successfully.")
            print(f"Object URL: {new_file_url}")
            return new_file_url
        except Exception as e:
            print(f"Error replacing email body: {e}")
            return None


    def download_attachments_from_s3(self, s3_file_urls, destination_folder):
        """
        Downloads attachment files from an S3 bucket and stores them in the specified local folder.

        :param s3_file_urls: List of URLs of the files in the S3 bucket.
        :param destination_folder: Local folder path where the downloaded files will be stored.
        :return: List of local file paths of the downloaded files if successful, else None.
        """
        downloaded_files = []
        try:
            for s3_file_url in s3_file_urls:
                # Extract bucket name and object key from the file URL
                bucket_name = s3_file_url.split('//')[1].split('.')[0]
                object_name = s3_file_url.split('.com/')[1]  # Get the object name directly

                # Check if the object exists in the bucket
                response = self.s3.head_object(Bucket=bucket_name, Key=object_name)

                # If object exists, proceed with the download
                # Extract folder and file name from the object name
                folder_name, file_name = os.path.split(object_name)

                # Construct the destination path including the "Attachments" folder
                destination_path = os.path.join(destination_folder, folder_name, file_name)

                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                # Download the file from S3
                self.s3.download_file(bucket_name, object_name, destination_path)
                print(f"Attachment '{object_name}' downloaded from '{bucket_name}' to '{destination_path}' successfully.")
                downloaded_files.append(destination_path)

            return downloaded_files
        except Exception as e:
            print(f"Error downloading attachments: {e}")
            return None

    def download_email_body_from_s3(self, s3_body_url):
        """
        Downloads an email body file from an S3 bucket and returns the decoded text.

        :param file_url: URL of the file in the S3 bucket.
        :return: Decoded text of the downloaded email body if successful, else None.
        """
        try:
            # Extract bucket name and object key from the file URL
            bucket_name = s3_body_url.split('//')[1].split('.')[0]
            object_name = s3_body_url.split('.com/')[1]  # Get the object name directly

            # Download the file from S3
            response = self.s3.get_object(Bucket=bucket_name, Key=object_name)

            # Read the content of the object and decode it from utf-8
            email_body_text = response['Body'].read().decode('utf-8')

            print(f"Email body '{object_name}' downloaded from '{bucket_name}' successfully.")
            return email_body_text
        except Exception as e:
            print(f"Error downloading email body: {e}")
            return None

    def delete_object_from_s3(self, s3_object_url):
        # Your delete logic here using self.s3
        """
        Deletes an object from an S3 bucket using its URL.

        :param file_url: URL of the object in the S3 bucket.
        :return: True if the object is successfully deleted, False otherwise.
        """
        try:

            bucket_name = s3_object_url.split('//')[1].split('.')[0]
            object_key = s3_object_url.split('.com/')[1]  # Get the object name directly

            # Delete the object from S3 bucket
            self.s3.delete_object(Bucket=bucket_name, Key=object_key)

            print(f"Object '{object_key}' deleted from '{bucket_name}' successfully.")
            return True
        except Exception as e:
            print(f"Error deleting object: {e}")
            return False

    def create_presigned_url(self, bucket_name, object_name, expiration=3600):
        """Generate a presigned URL to share an S3 object

        :param bucket_name: string
        :param object_name: string
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """

        # Generate a presigned URL for the S3 object
        # s3_client = boto3.client('s3',
        #                         aws_access_key_id=aws_access_key_id,
        #                         aws_secret_access_key=aws_secret_access_key,
        #                         region_name=region_name)

        # s3_client = boto3.client('s3')
        try:
            response = self.s3.generate_presigned_url('get_object',
                                                        Params={'Bucket': bucket_name,
                                                                'Key': object_name},
                                                        ExpiresIn=expiration)
            return response
        except ClientError as e:
            logging.error(e)
            return None

    def get_s3_file_metadata(self,bucket_name,object_name):

        # Get the object's metadata
        response = self.s3.head_object(Bucket=bucket_name, Key=object_name)

        return response

# TODO :: clarity regarding storing the credentials.
aws_access_key_id = settings.AWS_ACCESS_KEY_ID
aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
region_name = 'us-west-2'
aws_storage_bucket_name = 'connected-customer'

# Initialize the S3Manager instance with AWS credentials
# s3_manager = S3Manager(aws_access_key_id=aws_access_key_id,
#                        aws_secret_access_key=aws_secret_access_key,
#                        region_name=region_name)

# s3_object_url example
# s3_object_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"

