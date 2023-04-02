#Configuration of the EC2 instance used as a Bastion to connect to the private RDS instance
data "aws_ami" "linux" {
  most_recent = true

  filter {
    name   = "name"
    values = ["al2023-ami-2023.0.20230322.0-kernel-6.1-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["amazon"]
}

resource "aws_security_group" "bastion_sg" {
  name        = "bastion_ecowaterdb-${local.environment}"
  description = "Allow SSH traffic to EC2 Bastion"

  ingress {
    from_port   = "22"
    to_port     = "22"
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_kms_key" "ebs_key" {
  description             = "KMS key used to encrypt the EBS of the EC2 Bastion"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}

resource "aws_kms_alias" "ebs_key_alias" {
  name          = "alias/ebs_key-${local.name}-${local.environment}"
  target_key_id = aws_kms_key.ebs_key.key_id
}

resource "aws_instance" "bastion" {
  ami           = data.aws_ami.linux.id
  instance_type = "t2.nano"
  tags = {
    Name = "ecowaterdb_bastion-${local.environment}"
  }
  ebs_block_device {
    volume_type = "gp2"
    volume_size = 8
    device_name = "/dev/xvda"
    encrypted   = true
    kms_key_id  = aws_kms_key.ebs_key.key_id
  }
  associate_public_ip_address = true
  subnet_id                   = var.default_subnet_a_id
  vpc_security_group_ids      = [aws_security_group.bastion_sg.id]
}