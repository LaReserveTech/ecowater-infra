#Manage the default VPC and default subnets via terraform
resource "aws_default_vpc" "default" {}


resource "aws_default_subnet" "default_subnet_a" {
  availability_zone = "eu-west-3a"
  tags = {
    Type = "Public"
  }
}

resource "aws_default_subnet" "default_subnet_b" { #Manually removed the route to the Internet Gateway and added tag
  availability_zone = "eu-west-3b"
  tags = {
    Type = "Private"
  }
}

resource "aws_default_subnet" "default_subnet_c" { #Manually removed the route to the Internet Gateway and added tag
  availability_zone = "eu-west-3c"
  tags = {
    Type = "Private"
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "tag:Type"
    values = ["Private"]
  }

  depends_on = [
    aws_default_subnet.default_subnet_b,
    aws_default_subnet.default_subnet_c
  ]
}

#Private route table for the Ecowater DB instance's private subnet
resource "aws_route_table" "private-route" {
  count = local.environment == "dev" ? 1 : 0

  vpc_id = aws_default_vpc.default.id
  route {
    cidr_block     = "0.0.0.0/0" #For the Lambda to be reachable by the API
    nat_gateway_id = aws_nat_gateway.nat_gateway.id
  }
  #Route to local will be automatically added by terraform
  tags = {
    Name = "private-route"
  }
}

resource "aws_route_table_association" "private-route" {
  for_each = toset(data.aws_subnets.private.ids)

  subnet_id      = each.value
  route_table_id = aws_route_table.private-route[0].id
}

#Lambda network configuration
resource "aws_eip" "ngw_eip" {
  vpc = true
}

resource "aws_nat_gateway" "nat_gateway" {
  allocation_id = aws_eip.ngw_eip.id
  subnet_id     = aws_default_subnet.default_subnet_a.id #NAT must be in a public subnet
}

resource "aws_security_group" "lambda_zone_sg" {
  name        = "allow_lambda_zone_access-${local.environment}"
  description = "Allow traffic to Lambda in private subnet"

  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "tcp"
    self      = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}