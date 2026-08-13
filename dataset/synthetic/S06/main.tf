resource "aws_s3_bucket" "public_write" {
  bucket = "terraform-security-demo-public-write"
}

resource "aws_s3_bucket_public_access_block" "public_write" {
  bucket = aws_s3_bucket.public_write.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "public_write" {
  bucket = aws_s3_bucket.public_write.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:PutObject"
      Resource  = "${aws_s3_bucket.public_write.arn}/*"
    }]
  })
}

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "ap-southeast-2"
}