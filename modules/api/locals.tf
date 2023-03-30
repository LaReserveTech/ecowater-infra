data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "aws_apigatewayv2_apis" "zone_alert" {
  protocol_type = "HTTP"
  tags = {
    Project_tf_name = "ecowater"
    Environment     = "dev"
  }
}

locals {
  name            = "ecowater"
  environment     = terraform.workspace
  account_id      = data.aws_caller_identity.current.account_id
  region          = data.aws_region.current.id
  lambda_src_path = "${path.module}/lambda_code"
  zone_alert_api_id = element(tolist(data.aws_apigatewayv2_apis.zone_alert.ids), 0)
}