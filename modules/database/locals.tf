locals {
  allocated_storage = {
    "dev"  = 5
    "prod" = 5
  }
  max_allocated_storage = local.allocated_storage[local.environment] * 2
  name                  = "ecowater"
  environment           = terraform.workspace
}