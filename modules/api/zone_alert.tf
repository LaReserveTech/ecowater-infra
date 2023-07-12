#Lambda Layers
resource "aws_lambda_layer_version" "psycopg2_layer" {
  filename   = "${local.lambda_src_path}/psycopg2.zip"
  layer_name = "psycopg2-${local.environment}"

  compatible_runtimes = ["python3.9"]

  source_code_hash = filebase64sha256("${local.lambda_src_path}/psycopg2.zip")
}

resource "aws_lambda_layer_version" "getCredentials_layer" {
  filename   = abspath("${path.module}/common/db_connection.zip")
  layer_name = "db_connection-${local.environment}"

  compatible_runtimes = ["python3.9"]

  source_code_hash = filebase64sha256(abspath("${path.module}/common/db_connection.zip"))
}

#Lambda function for API integration with DB
resource "random_uuid" "lambda_src_hash" {
  keepers = {
    for filename in fileset("${local.lambda_src_path}/package/", "*.py") :
    filename => filemd5("${local.lambda_src_path}/package/${filename}")
  }
}

data "archive_file" "lambda_zip" {
  type             = "zip"
  source_dir       = "${local.lambda_src_path}/package/"
  output_file_mode = "0755"
  output_path      = "${local.lambda_src_path}/${local.environment}/${random_uuid.lambda_src_hash.result}.zip"

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
  memory_size            = 128
  timeout                = 10
  create_package         = false
  create_function        = true
  layers = [
    aws_lambda_layer_version.psycopg2_layer.arn,
    aws_lambda_layer_version.getCredentials_layer.arn,
  ]
  local_existing_package = "${local.lambda_src_path}/${local.environment}/${random_uuid.lambda_src_hash.result}.zip"
  publish                = true
  environment_variables = {
    env         = local.environment
    secret_name = "ecowater-${local.environment}"
    region_name = "eu-west-3"
    db          = local.name
    raw_path    = "/${local.environment}/zone"
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
  source_arn    = "arn:aws:execute-api:${local.region}:${local.account_id}:${aws_apigatewayv2_api.zone_alert.id}/*/*/zone"
}


#API Gateway configuration
resource "aws_apigatewayv2_api" "zone_alert" {
  name          = "${local.name}_api-${local.environment}"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["https://alerte-secheresse.fr", "https://eco-water.webflow.io"]
    allow_methods = ["GET", "OPTIONS"]
    allow_headers = ["Content-Type"]
    max_age       = 300
  }
}

resource "aws_apigatewayv2_integration" "zone_alert" {
  api_id                 = aws_apigatewayv2_api.zone_alert.id
  integration_type       = "AWS_PROXY"
  connection_type        = "INTERNET"
  description            = "Lambda integration for zone alert in ${local.environment}"
  integration_method     = "POST"
  integration_uri        = module.lambda_ecowater_zone.lambda_function_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "zone_alert" {
  api_id    = aws_apigatewayv2_api.zone_alert.id
  route_key = "GET /zone"
  target    = "integrations/${aws_apigatewayv2_integration.zone_alert.id}"
}

resource "aws_apigatewayv2_stage" "zone_alert_api_env" {
  api_id      = aws_apigatewayv2_api.zone_alert.id
  name        = local.environment
  auto_deploy = true
}