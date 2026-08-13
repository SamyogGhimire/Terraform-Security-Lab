variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_db_instance" "private" {
  identifier = "terraform-security-demo-private-db"

  engine         = "mysql"
  instance_class = "db.t3.micro"

  allocated_storage = 20

  username = "admin"
  password = var.db_password

  publicly_accessible     = false
  skip_final_snapshot     = false
  deletion_protection    = true
  backup_retention_period = 7
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