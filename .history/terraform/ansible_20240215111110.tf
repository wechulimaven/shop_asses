provider "aws" {
  region = "us-east-1" # Change to your desired region
}

resource "tls_private_key" "cicd_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "cicd_key" {
  key_name   = "CICD_KEY"
  public_key = tls_private_key.cicd_key.public_key_openssh
}

resource "aws_security_group" "cicd_sg" {
  name        = "CICD_Security_Group"
  description = "Security group for CICD"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "example" {
  ami             = "ami-0c55b159cbfafe1f0" # Amazon Linux 2 AMI (HVM), SSD Volume Type (Free Tier)
  instance_type   = "t2.micro" # Free Tier eligible instance type
  security_groups = [aws_security_group.cicd_sg.name]
  key_name        = aws_key_pair.cicd_key.key_name

  tags = {
    Name = "jenkinsServer"
  }
}
