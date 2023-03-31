module "common" {
  source = "./modules/common"
}

module "database" {
  source = "./modules/database"

  default_subnet_a_id = module.common.default_subnet_a_id
  private_subnets_ids = module.common.private_subnets_ids
  database_username   = var.database_username
  database_password   = var.database_password
  lambda_zone_sg_id   = module.common.lambda_zone_sg_id
}

module "api" {
  source = "./modules/api"

  default_subnet_c_id = module.common.default_subnet_c_id
  lambda_zone_sg_id   = module.common.lambda_zone_sg_id
  db_creds            = module.database.db_creds
  db_creds_kms        = module.database.db_creds_kms
}