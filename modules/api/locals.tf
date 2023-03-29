locals {
  name            = "ecowater"
  environment     = terraform.workspace
  lambda_src_path = "${path.module}/lambda_code"
}