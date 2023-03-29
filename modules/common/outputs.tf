output "default_vpc_id" {
  value = aws_default_vpc.default.id
}

output "default_subnet_a_id" {
  value = aws_default_subnet.default_subnet_a.id
}

output "default_subnet_b_id" {
  value = aws_default_subnet.default_subnet_b.id
}

output "default_subnet_c_id" {
  value = aws_default_subnet.default_subnet_c.id
}

output "lambda_zone_sg_id" {
  value = aws_security_group.lambda_zone_sg.id
}