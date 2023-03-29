output "database_sg_id" {
  value = aws_security_group.database_sg.id
}

output "db_creds" {
  value = aws_secretsmanager_secret.ecowater_db.arn
}

output "db_creds_kms" {
  value = aws_kms_key.ecowaterdb_creds.arn
}