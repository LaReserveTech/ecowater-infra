variable "default_subnet_c_id" {
  type = string
}

variable "lambda_zone_sg_id" {
  type = string
}

variable "db_creds" {
  type = string
}

variable "db_creds_kms" {
  type = string
}

variable "sub-domain" {
  type = map(string)
  default = {
    dev  = "api-dev.alerte-secheresse.fr"
    prod = "api.alerte-secheresse.fr"
  }
}

variable "cf-sub-domain" {
  type = map(string)
  default = {
    dev  = "alerte-secheresse-dev.eu.org"
    prod = "alerte-secheresse.eu.org"
  }
}

variable "db_arn" {
  type = string
}