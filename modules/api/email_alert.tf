#Lambda Layer (will be deployed only once to be used for both environments)
resource "aws_lambda_layer_version" "mailjet_libs_layer" {
  count = local.environment == "dev" ? 1 : 0

  filename   = "${local.email_src_path}/package/libs_mailjet.zip"
  layer_name = "libs_mailjet"

  compatible_runtimes = ["python3.9"]

  source_code_hash = filebase64sha256("${local.email_src_path}/package/libs_mailjet.zip")
}

#Lambda function for email alerting
resource "random_uuid" "email_src_hash" {
  keepers = {
    for filename in fileset("${local.email_src_path}", "*.py") :
    filename => filemd5("${local.email_src_path}/${filename}")
  }
}

data "archive_file" "email_zip" {
  type             = "zip"
  source_file      = "${local.email_src_path}/package/index.py"
  output_file_mode = "0755"
  output_path      = "${local.email_src_path}/${local.environment}/${random_uuid.email_src_hash.result}.zip"

  depends_on = [
    random_uuid.email_src_hash
  ]
}

module "lambda_email_alerting" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=v3.2.0"

  function_name          = "${local.name}_email-${local.environment}"
  description            = "Lambda function for sending emails when the alert level changes for a given zone"
  handler                = "index.lambda_handler"
  runtime                = "python3.9"
  create_role            = true
  attach_policy          = true
  policy                 = aws_iam_policy.lambda_email_alerting.arn
  attach_network_policy  = true
  attach_tracing_policy  = true
  vpc_subnet_ids         = [var.default_subnet_c_id] #linked to just one private subnet (the same as the DB), keeping the other as a backup/for tests
  vpc_security_group_ids = [var.lambda_zone_sg_id]
  memory_size            = 200
  timeout                = 30
  create_package         = false
  create_function        = true
  layers = [
    aws_lambda_layer_version.psycopg2_layer[0].arn,
    aws_lambda_layer_version.getCredentials_layer[0].arn,
    aws_lambda_layer_version.mailjet_libs_layer[0].arn,
  ]
  local_existing_package = "${local.email_src_path}/${local.environment}/${random_uuid.email_src_hash.result}.zip"
  publish                = true
  environment_variables = {
    secret_name = "ecowater-${local.environment}"
    region_name = "eu-west-3"
    db          = local.name
  }
}

resource "aws_lambda_alias" "lambda_email_alerting" {
  name             = "latest-${local.name}_email-${local.environment}"
  description      = "Alias for the Lambda function for email alerting"
  function_name    = module.lambda_email_alerting.lambda_function_name
  function_version = "$LATEST"

  depends_on = [
    module.lambda_email_alerting
  ]
}

resource "aws_iam_policy" "lambda_email_alerting" {
  name   = "lambda_${local.name}_email-${local.environment}"
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

resource "aws_lambda_permission" "email_alerting" {
  statement_id  = "AllowExecutionFromRDS"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_email_alerting.lambda_function_name
  principal     = "rds.amazonaws.com"
  source_arn    = var.db_arn
}
