#Lambda function for API integration with DB

resource "random_uuid" "lambda_src_hash" {
  keepers = {
    for filename in fileset(local.lambda_src_path, "*.py") :
    filename => filemd5("${local.lambda_src_path}/${filename}")
  }
}

data "archive_file" "lambda_zip" {
  type             = "zip"
  source_dir      = "${local.lambda_src_path}/package"
  output_file_mode = "0755"
  output_path      = "${local.lambda_src_path}/${random_uuid.lambda_src_hash.result}.zip"

  depends_on = [
    random_uuid.lambda_src_hash
  ]
}

module "lambda_ecowater_zone" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=v3.2.0"

  function_name          = "${local.name}_zone-${local.environment}"
  description            = "Lambda function for API integration with Ecowater's DB"
  handler                = "index.lambda_handler"
  runtime                = "python3.9"
  create_role            = true
  attach_policy          = true
  policy                 = aws_iam_policy.lambda_ecowater_zone.arn
  attach_network_policy  = true
  attach_tracing_policy  = true
  vpc_subnet_ids         = [var.default_subnet_c_id] #linked to just one private subnet (the same as the DB), keeping the other as a backup/for tests
  vpc_security_group_ids = [var.lambda_zone_sg_id]
  memory_size            = 512
  timeout                = 60
  create_package         = false
  create_function        = true
  local_existing_package = "${local.lambda_src_path}/${random_uuid.lambda_src_hash.result}.zip"
  publish                = true
  environment_variables = {
    environment = local.environment
  }
}

resource "aws_lambda_alias" "lambda_ecowater_zone" {
  name             = "latest-${local.name}_zone-${local.environment}"
  description      = "Alias for the Lambda function integrating the API (zone) with Ecowater's DB"
  function_name    = module.lambda_ecowater_zone.lambda_function_name
  function_version = "$LATEST"

  depends_on = [
    module.lambda_ecowater_zone
  ]
}

resource "aws_iam_policy" "lambda_ecowater_zone" {
  name   = "lambda_ecowater_zone-${local.environment}"
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

resource "aws_lambda_permission" "zone_alert" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_ecowater_zone.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  #source_arn    = "${aws_apigatewayv2_api.zone_alert.arn}/*"  doesn't seem to work
}


#API Gateway configuration
resource "aws_apigatewayv2_api" "zone_alert" {
  name          = "${local.name}_zone-${local.environment}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_route" "zone_alert" {
  api_id    = aws_apigatewayv2_api.zone_alert.id
  route_key = "GET /zone"
  target    = "integrations/${aws_apigatewayv2_integration.zone_alert.id}"
}

resource "aws_apigatewayv2_integration" "zone_alert" {
  api_id                 = aws_apigatewayv2_api.zone_alert.id
  integration_type       = "AWS_PROXY"
  connection_type        = "INTERNET"
  description            = "Lambda integration for zone alert"
  integration_method     = "POST"
  integration_uri        = module.lambda_ecowater_zone.lambda_function_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_stage" "zone_alert_api_env" {
  api_id = aws_apigatewayv2_api.zone_alert.id
  name   = local.environment
}