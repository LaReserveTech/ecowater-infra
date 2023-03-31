#Manage the default VPC and default subnets via terraform
resource "aws_default_vpc" "default" {
  count = local.environment == "dev" ? 1 : 0
}


resource "aws_default_subnet" "default_subnet_a" {
  count = local.environment == "dev" ? 1 : 0

  availability_zone = "eu-west-3a"
  tags = {
    Type = "Public"
  }
}

resource "aws_default_subnet" "default_subnet_b" { #Manually removed the route to the Internet Gateway and added tag
  count = local.environment == "dev" ? 1 : 0

  availability_zone = "eu-west-3b"
  tags = {
    Type = "Private"
  }
}

resource "aws_default_subnet" "default_subnet_c" { #Manually removed the route to the Internet Gateway and added tag
  count = local.environment == "dev" ? 1 : 0

  availability_zone = "eu-west-3c"
  tags = {
    Type = "Private"
  }
}

#Private route table for the Ecowater DB instance's private subnet
resource "aws_route_table" "private-route" {
  count = local.environment == "dev" ? 1 : 0

  vpc_id = aws_default_vpc.default[0].id
  route {
    cidr_block     = "0.0.0.0/0" #For the Lambda to be reachable by the API
    nat_gateway_id = aws_nat_gateway.nat_gateway[0].id
  }
  #Route to local will be automatically added by terraform
  tags = {
    Name = "private-route"
  }
}

resource "aws_route_table_association" "private-route-b" {
  count = local.environment == "dev" ? 1 : 0

  subnet_id      = aws_default_subnet.default_subnet_b[0].id
  route_table_id = aws_route_table.private-route[0].id
}

resource "aws_route_table_association" "private-route-c" {
  count = local.environment == "dev" ? 1 : 0

  subnet_id      = aws_default_subnet.default_subnet_c[0].id
  route_table_id = aws_route_table.private-route[0].id
}

#Lambda network configuration
resource "aws_eip" "ngw_eip" {
  count = local.environment == "dev" ? 1 : 0
  vpc   = true
}

resource "aws_nat_gateway" "nat_gateway" {
  count = local.environment == "dev" ? 1 : 0

  allocation_id = aws_eip.ngw_eip[0].id
  subnet_id     = aws_default_subnet.default_subnet_a[0].id #NAT must be in a public subnet
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