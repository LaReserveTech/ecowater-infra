variable "default_subnet_a_id" {
  type = string
}

variable "private_subnets_ids" {
  type = list(any)
}

variable "database_username" {
  type      = string
  sensitive = true
}

variable "database_password" {
  type      = string
  sensitive = true
}

#variable "read_replica1_username" {
#  type      = string
#  sensitive = true
#}
#
#variable "read_replica1_password" {
#  type      = string
#  sensitive = true
#}

variable "database_port" {
  type    = number
  default = 5432
}

variable "lambda_zone_sg_id" {
  type = string
}

variable "example_secret" {
  type = map(any)
  default = {
    key1 = "value1"
  }
}