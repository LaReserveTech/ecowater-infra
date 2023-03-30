output "default_vpc_id" {
  value = aws_default_vpc.default.id
}

output "default_subnet_a_id" {
  value = length(aws_default_subnet.default_subnet_a) > 0 ? aws_default_subnet.default_subnet_a[0].id : ""
}

output "default_subnet_b_id" {
  value = length(aws_default_subnet.default_subnet_b) > 0 ? aws_default_subnet.default_subnet_b[0].id : ""
}

output "default_subnet_c_id" {
  value = length(aws_default_subnet.default_subnet_c) > 0 ? aws_default_subnet.default_subnet_c[0].id : ""
}

output "lambda_zone_sg_id" {
  value = aws_security_group.lambda_zone_sg.id
}