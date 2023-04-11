resource "aws_security_group" "database_sg" {
  name        = "allow_ecowaterdb_access-${local.environment}"
  description = "Allow database inbound traffic"

  ingress {
    from_port       = var.database_port
    to_port         = var.database_port
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion_sg.id] #EC2 security group
  }

  ingress {
    from_port       = var.database_port
    to_port         = var.database_port
    protocol        = "tcp"
    security_groups = [var.lambda_zone_sg_id] #Lambda security group
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
  }
}

resource "aws_db_instance" "ecowater" {
  identifier              = "${local.name}-${local.environment}"
  storage_encrypted       = true
  allocated_storage       = local.allocated_storage[local.environment]
  max_allocated_storage   = local.max_allocated_storage
  backup_retention_period = 7

  instance_class              = "db.t3.micro"
  engine                      = "postgres"
  engine_version              = "14.4"
  port                        = var.database_port
  auto_minor_version_upgrade  = false
  allow_major_version_upgrade = false


  db_name  = local.name
  username = var.database_username
  password = var.database_password

  skip_final_snapshot = true
  maintenance_window  = "Sat:02:00-Sat:05:00"

  apply_immediately = true

  publicly_accessible    = false
  availability_zone      = "eu-west-3c"
  vpc_security_group_ids = [aws_security_group.database_sg.id]
}

resource "aws_db_instance" "read-replica1-ecowater" {
  count = local.environment == "prod" ? 1 : 0

  identifier              = "read-replica1-${local.name}-${local.environment}"
  storage_encrypted       = true
  backup_retention_period = 7

  instance_class              = "db.t3.xlarge"
  port                        = var.database_port
  auto_minor_version_upgrade  = false
  allow_major_version_upgrade = false

  replicate_source_db = aws_db_instance.ecowater.identifier

  skip_final_snapshot = true
  maintenance_window  = "Sat:02:00-Sat:05:00"

  apply_immediately = true

  publicly_accessible    = false
  availability_zone      = "eu-west-3c"
  vpc_security_group_ids = [aws_security_group.database_sg.id]
}

#Store the database credentials in AWS (the value of the credential will be added manually, only a placeholder is deployed)

resource "aws_secretsmanager_secret" "ecowater_db" {
  name       = "${local.name}-${local.environment}"
  kms_key_id = aws_kms_key.ecowaterdb_creds.arn
}

resource "aws_secretsmanager_secret_version" "example" {
  secret_id     = aws_secretsmanager_secret.ecowater_db.id
  secret_string = jsonencode(var.example_secret)
}

resource "aws_kms_key" "ecowaterdb_creds" {
  description         = "KMS key used to encrypt the credentials of Ecowater's RDS DB inside Secrets Manager"
  enable_key_rotation = true
}

resource "aws_kms_alias" "ecowaterdb_creds" {
  name          = "alias/ecowaterdb_creds-${local.name}-${local.environment}"
  target_key_id = aws_kms_key.ecowaterdb_creds.key_id
}