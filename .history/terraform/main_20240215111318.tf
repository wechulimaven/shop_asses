 # THIS TERRAFORM IS USED TO PROVISSION 3 AWS EC2 INSTANSES

provider "aws" {
  region = "us-east-1"
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

variable "instance_count" {
  description = "Number of EC2 instances to create"
  type        = number
  default     = 3
}

variable "instance_tags" {
  description = "Map of instance names"
  type        = map(string)
  default     = {
    "AnsibleServer"    = "ansible_server"
    "KubernetesServer" = "kubernetes_server"
    "JenkinsServer"    = "jenkins_server"
  }
}

resource "aws_instance" "example" {
  count          = var.instance_count
  ami            = "ami-0c55b159cbfafe1f0" # Amazon Linux 2 AMI (HVM), SSD Volume Type (Free Tier)
  instance_type  = "t2.micro" # Free Tier eligible instance type
  security_groups = [aws_security_group.cicd_sg.name]
  key_name       = aws_key_pair.cicd_key.key_name
  tags = {
    Name = var.instance_tags["${element(keys(var.instance_tags), count.index)}"]
  }
}
