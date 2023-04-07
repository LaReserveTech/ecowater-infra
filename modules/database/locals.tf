locals {
  allocated_storage = {
    "dev" = 5
    "pro" = 5
  }
  max_allocated_storage = local.allocated_storage[terraform.workspace] * 2
  name                  = "ecowater"
  environment           = terraform.workspace
}