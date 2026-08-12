variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_db_instance" "secure" {
  identifier          = "secure-demo-db"
  engine              = "mysql"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "admin"
  password            = var.db_password
  skip_final_snapshot = true
}
