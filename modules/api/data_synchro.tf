#Lambda function for DB data synchronisation
resource "random_uuid" "data_synchro_src_hash" {
  keepers = {
    for filename in fileset("${local.data_synchro_src_path}/package", "*.py") :
    filename => filemd5("${local.data_synchro_src_path}/package/${filename}")
  }
}

data "template_file" "synchro_code" {
  count = length(local.data_synchro_src_files)

  template = file(element(local.data_synchro_src_files, count.index))
}

data "archive_file" "data_synchro_zip" {
  type = "zip"
  source {
    filename = basename(local.data_synchro_src_files[0])
    content  = data.template_file.t_file.0.rendered
  }

  source {
    filename = basename(local.data_synchro_src_files[1])
    content  = data.template_file.t_file.1.rendered
  }

  source {
    filename = basename(local.data_synchro_src_files[2])
    content  = data.template_file.t_file.0.rendered
  }

  source {
    filename = basename(local.data_synchro_src_files[3])
    content  = data.template_file.t_file.1.rendered
  }

  source {
    filename = basename(local.data_synchro_src_files[4])
    content  = data.template_file.t_file.1.rendered
  }
  output_file_mode = "0755"
  output_path      = "${local.data_synchro_src_path}/${local.environment}/${random_uuid.data_synchro_src_hash.result}.zip"

  depends_on = [
    random_uuid.data_synchro_src_hash
  ]
}

module "lambda_data_synchro" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-lambda.git?ref=v3.2.0"

  function_name          = "${local.name}_data_synchro-${local.environment}"
  description            = "Lambda function for DB data synchronisation"
  handler                = "index.lambda_handler"
  runtime                = "python3.9"
  create_role            = true
  attach_policy          = true
  policy                 = aws_iam_policy.lambda_data_synchro.arn
  attach_network_policy  = true
  attach_tracing_policy  = true
  vpc_subnet_ids         = [var.default_subnet_c_id] #linked to just one private subnet (the same as the DB), keeping the other as a backup/for tests
  vpc_security_group_ids = [var.lambda_zone_sg_id]
  memory_size            = 128
  timeout                = 30
  create_package         = false
  create_function        = true
  layers = [
    aws_lambda_layer_version.psycopg2_layer[0].arn,
    aws_lambda_layer_version.getCredentials_layer[0].arn,
  ]
  local_existing_package = "${local.data_synchro_src_path}/${local.environment}/${random_uuid.data_synchro_src_hash.result}.zip"
  allowed_triggers = {
    EventsCron = {
      principal  = "events.amazonaws.com"
      source_arn = aws_cloudwatch_event_rule.lambda_scheduling.arn
    }
  }
  environment_variables = {
    secret_name = "ecowater-${local.environment}"
    region_name = "eu-west-3"
    db          = local.name
  }
  publish = true
}

resource "aws_lambda_alias" "lambda_data_synchro" {
  name             = "latest-${local.name}_data_synchro-${local.environment}"
  description      = "Alias of the Lambda function for DB data synchronisation"
  function_name    = module.lambda_data_synchro.lambda_function_name
  function_version = "$LATEST"

  depends_on = [
    module.lambda_data_synchro
  ]
}

resource "aws_iam_policy" "lambda_data_synchro" {
  name   = "lambda_${local.name}_data_synchro-${local.environment}"
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

#CloudWatch Events

resource "aws_cloudwatch_event_rule" "lambda_scheduling" {
  name           = "${local.name}-data_synchro-${local.environment}"
  description    = "Triggers the synchronisation of the DB"
  event_bus_name = "default"

  schedule_expression = "cron(0 0 * * ? *)"

  is_enabled = local.enable_cron[local.environment]
}