data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  name                       = "ecowater"
  environment                = terraform.workspace
  account_id                 = data.aws_caller_identity.current.account_id
  region                     = data.aws_region.current.id
  lambda_src_path            = "${path.module}/lambda_code"
  email_src_path             = "${path.module}/email_alerting_code"
  email_sub_src_path         = "${path.module}/email_sub_code"
  data_synchro_src_path      = "${path.module}/sync"
  alert_level_zones_src_path = "${path.module}/global_zones"
}