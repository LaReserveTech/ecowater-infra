variable "aws_region" {
  type    = string
  default = "eu-west-3"
}

variable "project_tf_name" {
  type    = string
  default = "ecowater"
}

variable "stack" {
  type    = string
  default = "infra"
}

variable "database_username" {
  type      = string
  sensitive = true
}

variable "database_password" {
  type      = string
  sensitive = true
}