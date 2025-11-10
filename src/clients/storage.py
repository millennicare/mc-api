import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile

from src.core.config import storage_settings
from src.core.logger import setup_logger


class StorageClient:
    def __init__(self):
        """
        Initialize the storage client for Cloudflare R2.

        Args:
            account_id: Cloudflare account ID
            access_key_id: R2 access key ID
            secret_access_key: R2 secret access key
            bucket_name: Name of the R2 bucket
        """
        self.bucket_name = storage_settings.cloudflare_bucket_name
        self.logger = setup_logger(__name__)

        # Initialize S3 client with R2 endpoint
        self.client = boto3.client(
            "s3",
            endpoint_url=f"https://{storage_settings.cloudflare_account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=storage_settings.cloudflare_access_key_id,
            aws_secret_access_key=storage_settings.cloudflare_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )

    async def upload_file(
        self,
        file: UploadFile,
        key: str,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """
        Upload a file to R2 storage.

        Args:
            file: File-like object to upload
            key: Object key (path) in the bucket
            content_type: MIME type of the file
            metadata: Optional metadata to attach to the file

        Returns:
            The key of the uploaded file

        Raises:
            ClientError: If upload fails
        """
        try:
            # FastAPI's UploadFile.file is a SpooledTemporaryFile which is file-like
            # Read position should be at the start, but reset to be safe
            await file.seek(0)

            extra_args = {}
            if file.content_type:
                extra_args["ContentType"] = file.content_type
            if metadata:
                extra_args["Metadata"] = metadata

            self.client.upload_fileobj(
                file.file,
                self.bucket_name,
                key,
                ExtraArgs=extra_args if extra_args else None,
            )

            self.logger.info(
                f"StorageClient . upload_fastapi_file . Uploaded {file.filename} to {key}"
            )
            return key

        except ClientError as e:
            self.logger.error(
                f"StorageClient . upload_fastapi_file . Failed to upload {key}: {str(e)}"
            )
            raise

    def get_presigned_url(
        self,
        key: str,
        expiration: int = 3600,
        response_content_disposition: str | None = None,
    ) -> str:
        """
        Generate a presigned URL for file access.

        Args:
            key: Object key (path) in the bucket
            expiration: URL expiration time in seconds (default: 1 hour)
            response_content_disposition: Optional Content-Disposition header

        Returns:
            Presigned URL string

        Raises:
            ClientError: If URL generation fails
        """
        try:
            params = {
                "Bucket": self.bucket_name,
                "Key": key,
            }

            if response_content_disposition:
                params["ResponseContentDisposition"] = response_content_disposition

            url = self.client.generate_presigned_url(
                "get_object",
                Params=params,
                ExpiresIn=expiration,
            )

            self.logger.info(
                f"StorageClient . get_presigned_url . Generated presigned URL for {key}"
            )
            return url

        except ClientError as e:
            self.logger.error(
                f"StorageClient . get_presigned_url . Failed to generate URL for {key}: {str(e)}"
            )
            raise

    def delete_file(self, key: str) -> None:
        """
        Delete a file from R2 storage.

        Args:
            key: Object key (path) in the bucket

        Raises:
            ClientError: If deletion fails
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )

            self.logger.info(f"StorageClient . delete_file . Deleted file {key}")

        except ClientError as e:
            self.logger.error(
                f"StorageClient . delete_file . Failed to delete {key}: {str(e)}"
            )
            raise

    def file_exists(self, key: str) -> bool:
        """
        Check if a file exists in R2 storage.

        Args:
            key: Object key (path) in the bucket

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            self.logger.error(
                f"StorageClient . file_exists . Error checking {key}: {str(e)}"
            )
            raise

    def get_file_metadata(self, key: str) -> dict:
        """
        Get metadata for a file in R2 storage.

        Args:
            key: Object key (path) in the bucket

        Returns:
            Dictionary containing file metadata

        Raises:
            ClientError: If file doesn't exist or retrieval fails
        """
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=key,
            )

            return {
                "content_type": response.get("ContentType"),
                "content_length": response.get("ContentLength"),
                "last_modified": response.get("LastModified"),
                "metadata": response.get("Metadata", {}),
                "etag": response.get("ETag"),
            }

        except ClientError as e:
            self.logger.error(
                f"StorageClient . get_file_metadata . Failed to get metadata for {key}: {str(e)}"
            )
            raise
