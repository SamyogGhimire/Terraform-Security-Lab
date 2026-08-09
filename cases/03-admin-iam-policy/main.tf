resource "aws_iam_policy" "admin_policy" {
  name = "research-admin-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = "*", Resource = "*" }]
  })
}
