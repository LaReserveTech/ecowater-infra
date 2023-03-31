output "default_vpc_id" {
  value = length(aws_default_vpc.default) > 0 ? aws_default_vpc.default[0].id : ""
}

output "default_subnet_a_id" {
  value = sort(data.aws_subnets.public.ids)[0]
}

output "default_subnet_b_id" {
  value = sort(data.aws_subnets.private.ids)[0]
}

output "default_subnet_c_id" {
  value = sort(data.aws_subnets.private.ids)[1]
}

output "private_subnets_ids" {
  value = tolist(data.aws_subnets.private.ids)
}

output "lambda_zone_sg_id" {
  value = aws_security_group.lambda_zone_sg.id
}