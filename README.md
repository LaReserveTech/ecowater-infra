# ecowater-infra

This repository describes the needed infrastructure to operate the Ecowater product.

The infrastructure is managed by Terraform.
The state is stored on S3.

# Requirements

- An existing S3 bucket.

# How to use this repo locally?

- Copy environment file: `cp .env.template .env`
- Replace environment variables with yours
- Source it: `source .env`
- Init terraform workdir: `terraform init -backend-config="bucket=$S3_BUCKET" -backend-config="region=$S3_REGION" -backend-config="dynamodb_table=$DYNAMODB"`
- Create new workspace `terraform workspace new <your-workspace>`
- Plan, apply as usual