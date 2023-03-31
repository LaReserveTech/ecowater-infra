module "common" {
  source = "./modules/common"
}

module "database" {
  source = "./modules/database"

  default_subnet_a_id = module.common.default_subnet_a_id
  database_username   = var.database_username
  database_password   = var.database_password
  lambda_zone_sg_id   = module.common.lambda_zone_sg_id
}

module "api" {
  source = "./modules/api"

  lambda_zone_sg_id = module.common.lambda_zone_sg_id
  db_creds          = module.database.db_creds
  db_creds_kms      = module.database.db_creds_kms
}