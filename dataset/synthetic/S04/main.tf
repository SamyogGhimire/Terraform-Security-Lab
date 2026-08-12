variable "username" {
  default = "admin"
}

resource "aws_db_instance" "example" {
  identifier          = "security-demo-db"
  engine              = "mysql"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "admin"
  password            = "SuperSecretPassword123!"
  skip_final_snapshot = true
}
