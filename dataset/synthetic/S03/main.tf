resource "aws_iam_role_policy" "admin_policy" {
  name = "admin-policy"
  role = "example-role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"
      Resource = "*"
    }]
  })
}
