data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  name                  = "ecowater"
  environment           = terraform.workspace
  account_id            = data.aws_caller_identity.current.account_id
  region                = data.aws_region.current.id
  lambda_src_path       = "${path.module}/lambda_code"
  email_src_path        = "${path.module}/email_alerting_code"
  email_sub_src_path    = "${path.module}/email_sub_code"
  data_synchro_src_path = "${path.module}/sync"
  data_synchro_src_files = ["${local.data_synchro_src_path}/package/index.py", "${local.data_synchro_src_path}/decree_provider.py", "${local.data_synchro_src_path}/package/decree_repository.py", "${local.data_synchro_src_path}/restriction_provider.py", "${local.data_synchro_src_path}/package/restriction_repository.py", "${local.data_synchro_src_path}/package/requirements.txt"]

  enable_cron = {
    "dev" = false
    "pro" = true
  }
}