resource "aws_db_instance" "public" {
  identifier = "terraform-security-demo-public-db"

  engine         = "mysql"
  instance_class = "db.t3.micro"

  allocated_storage = 20

  username = "admin"
  password = "SuperSecretPassword123!"

  publicly_accessible    = true
  skip_final_snapshot    = true
  deletion_protection   = false
  backup_retention_period = 0
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