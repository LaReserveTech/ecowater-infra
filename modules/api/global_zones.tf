#Lambda function for getting the total number of zones that are in alert
resource "random_uuid" "alert_level_zones_src_hash" {
  keepers = {
    for filename in fileset("${local.alert_level_zones_src_path}", "*.py") :
    filename => filemd5("${local.alert_level_zones_src_path}/${filename}")
  }
}

data "archive_file" "alert_level_zones_zip" {
  type             = "zip"
  source_file      = "${local.alert_level_zones_src_path}/package/index.py"
  output_file_mode = "0755"
  output_path      = "${local.alert_level_zones_src_path}/${local.environment}/${random_uuid.alert_level_zones_src_hash.result}.zip"

  depends_on = [
    random_uuid.alert_level_zones_src_hash
  ]
}

module "lambda_alert_level_zones" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=v3.2.0"

  function_name          = "${local.name}_alert_level_zones-${local.environment}"
  description            = "Lambda function for getting the total number of zones that are in alert"
  handler                = "index.lambda_handler"
  runtime                = "python3.9"
  create_role            = true
  attach_policy          = true
  policy                 = aws_iam_policy.lambda_alert_level_zones.arn
  attach_network_policy  = true
  attach_tracing_policy  = true
  vpc_subnet_ids         = [var.default_subnet_c_id] #linked to just one private subnet (the same as the DB), keeping the other as a backup/for tests
  vpc_security_group_ids = [var.lambda_zone_sg_id]
  memory_size            = 128
  timeout                = 10
  create_package         = false
  create_function        = true
  layers = [
    aws_lambda_layer_version.psycopg2_layer.arn,
    aws_lambda_layer_version.getCredentials_layer.arn,
  ]
  local_existing_package = "${local.alert_level_zones_src_path}/${local.environment}/${random_uuid.alert_level_zones_src_hash.result}.zip"
  publish                = true
  environment_variables = {
    env         = local.environment
    secret_name = "ecowater-${local.environment}"
    region_name = "eu-west-3"
    db          = local.name
    raw_path    = "/${local.environment}/global"
  }
}

resource "aws_lambda_alias" "lambda_alert_level_zones" {
  name             = "latest-${local.name}_alert_level_zones-${local.environment}"
  description      = "Alias for the Lambda function for getting the total zones that are in alert"
  function_name    = module.lambda_alert_level_zones.lambda_function_name
  function_version = "$LATEST"

  depends_on = [
    module.lambda_alert_level_zones
  ]
}

resource "aws_iam_policy" "lambda_alert_level_zones" {
  name   = "lambda_${local.name}_alert_level_zones-${local.environment}"
  policy = <<EOF
{
  "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": [
                "${var.db_creds}"
              ]
        },
        {
            "Effect": "Allow",
            "Action": [
              "kms:Decrypt"
            ],
            "Resource": "${var.db_creds_kms}"
        }
  ]
}
EOF
}

resource "aws_lambda_permission" "alert_level_zones" {
  statement_id  = "AllowExecutionFromRDS"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_alert_level_zones.lambda_function_name
  principal     = "rds.amazonaws.com"
  source_arn    = var.db_arn
}

#API configuration is in zone_alert.tf (same API for "global zones" and "zones" lambdas), 
#the following are the stages and routes for the "global zones" lambda integration

resource "aws_apigatewayv2_integration" "alert_level_zones" {
  api_id                 = aws_apigatewayv2_api.zone_alert.id
  integration_type       = "AWS_PROXY"
  connection_type        = "INTERNET"
  description            = "Lambda integration for global zones counting in ${local.environment}"
  integration_method     = "POST"
  integration_uri        = module.lambda_alert_level_zones.lambda_function_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "alert_level_zones" {
  api_id    = aws_apigatewayv2_api.zone_alert.id
  route_key = "GET /global"
  target    = "integrations/${aws_apigatewayv2_integration.alert_level_zones.id}"
}