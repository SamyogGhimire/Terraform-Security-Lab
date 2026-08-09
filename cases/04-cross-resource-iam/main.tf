resource "aws_iam_policy" "launch_policy" {
  name = "research-launch-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["iam:PassRole", "ec2:RunInstances"]
      Resource = "*"
    }]
  })
}
