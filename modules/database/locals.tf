locals {
  allocated_storage     = 10
  max_allocated_storage = local.allocated_storage * 2
  name                  = "ecowater"
  environment           = terraform.workspace
}