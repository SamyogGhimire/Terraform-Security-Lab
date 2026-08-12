resource "aws_iam_role_policy" "limited_policy" {
  name = "limited-policy"
  role = "example-role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = "arn:aws:s3:::example-bucket/*"
    }]
  })
}
