locals {
  environment = terraform.workspace
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project_tf_name = var.project_tf_name
      Stack           = var.stack
      Environment     = local.environment
    }
  }
}

terraform {
  required_version = ">= 1.3.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.50.0"
    }

    template = {
      source  = "hashicorp/template"
      version = "2.2.0"
    }
  }

  backend "s3" {
    key = "infra/terraform.tfstate"
  }
}