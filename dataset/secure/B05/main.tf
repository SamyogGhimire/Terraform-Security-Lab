resource "aws_s3_bucket" "encrypted" {
  bucket = "terraform-security-demo-encrypted"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encrypted" {
  bucket = aws_s3_bucket.encrypted.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
