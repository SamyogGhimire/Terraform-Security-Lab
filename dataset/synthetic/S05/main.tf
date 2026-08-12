resource "aws_s3_bucket" "unencrypted" {
  bucket = "terraform-security-demo-unencrypted"

  tags = {
    Name = "Unencrypted Bucket"
  }
}
