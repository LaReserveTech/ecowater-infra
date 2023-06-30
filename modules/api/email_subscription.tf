#Lambda Layer
resource "aws_lambda_layer_version" "email_validator_layer" {
  filename   = "${local.email_sub_src_path}/package/email_validator.zip"
  layer_name = "email_validator-${local.environment}"

  compatible_runtimes = ["python3.9"]

  source_code_hash = filebase64sha256("${local.email_sub_src_path}/package/email_validator.zip")
}

#Lambda function for email alerting
resource "random_uuid" "email_sub_src_hash" {
  keepers = {
    for filename in fileset("${local.email_sub_src_path}/package", "*.py") :
    filename => filemd5("${local.email_sub_src_path}/package/${filename}")
  }
}

data "archive_file" "email_sub_zip" {
  type             = "zip"
  source_file      = "${local.email_sub_src_path}/package/index.py"
  output_file_mode = "0755"
  output_path      = "${local.email_sub_src_path}/${local.environment}/${random_uuid.email_sub_src_hash.result}.zip"

  depends_on = [
    random_uuid.email_sub_src_hash
  ]
}

module "lambda_email_subscription" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=v3.2.0"

  function_name          = "${local.name}_email_sub-${local.environment}"
  description            = "Lambda function for email subscription"
  handler                = "index.lambda_handler"
  runtime                = "python3.9"
  create_role            = true
  attach_policy          = true
  policy                 = aws_iam_policy.lambda_email_subscription.arn
  attach_network_policy  = true
  attach_tracing_policy  = true
  vpc_subnet_ids         = [var.default_subnet_c_id] #linked to just one private subnet (the same as the DB), keeping the other as a backup/for tests
  vpc_security_group_ids = [var.lambda_zone_sg_id]
  memory_size            = 128
  timeout                = 30
  create_package         = false
  create_function        = true
  layers = [
    aws_lambda_layer_version.psycopg2_layer.arn,
    aws_lambda_layer_version.getCredentials_layer.arn,
    aws_lambda_layer_version.email_validator_layer.arn,
  ]
  local_existing_package = "${local.email_sub_src_path}/${local.environment}/${random_uuid.email_sub_src_hash.result}.zip"
  publish                = true
  environment_variables = {
    secret_name = "ecowater-${local.environment}"
    region_name = "eu-west-3"
    db          = local.name
    raw_path    = "/${local.environment}/subscription"
  }
}

resource "aws_lambda_alias" "lambda_email_subscription" {
  name             = "latest-${local.name}_email_sub-${local.environment}"
  description      = "Alias for the Lambda function for email subscription"
  function_name    = module.lambda_email_subscription.lambda_function_name
  function_version = "$LATEST"

  depends_on = [
    module.lambda_email_subscription
  ]
}

resource "aws_iam_policy" "lambda_email_subscription" {
  name   = "lambda_${local.name}_email_sub-${local.environment}"
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

resource "aws_lambda_permission" "email_subscription" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_email_subscription.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${local.region}:${local.account_id}:${aws_apigatewayv2_api.email_subscription.id}/*/*/subscription"
}

#API Gateway configuration
resource "aws_apigatewayv2_api" "email_subscription" {
  name          = "${local.name}_email_subscription-${local.environment}"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["http://alerte-secheresse.fr", "https://eco-water.webflow.io"]
    allow_methods = ["POST", "OPTIONS"]
    allow_headers = ["Content-Type"]
    max_age       = 300
  }
}

resource "aws_apigatewayv2_integration" "email_subscription" {
  api_id                 = aws_apigatewayv2_api.email_subscription.id
  integration_type       = "AWS_PROXY"
  connection_type        = "INTERNET"
  description            = "Lambda integration for email subscription in ${local.environment}"
  integration_method     = "POST"
  integration_uri        = module.lambda_email_subscription.lambda_function_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "email_subscription" {
  api_id    = aws_apigatewayv2_api.email_subscription.id
  route_key = "POST /subscription"
  target    = "integrations/${aws_apigatewayv2_integration.email_subscription.id}"
}

resource "aws_apigatewayv2_stage" "email_subscription_api_env" {
  api_id      = aws_apigatewayv2_api.email_subscription.id
  name        = local.environment
  auto_deploy = true
}