#SUBDOMAIN DELEGATION FOR API
resource "aws_route53_zone" "api-ecowater" {
  name = var.sub-domain[terraform.workspace]
}

resource "aws_route53_record" "api-ecowater" {
  allow_overwrite = true
  name            = var.sub-domain[terraform.workspace]
  ttl             = 172800
  type            = "NS"
  zone_id         = aws_route53_zone.api-ecowater.zone_id

  records = [
    aws_route53_zone.api-ecowater.name_servers[0],
    aws_route53_zone.api-ecowater.name_servers[1],
    aws_route53_zone.api-ecowater.name_servers[2],
    aws_route53_zone.api-ecowater.name_servers[3],
  ]
}

#SUBDOMAIN DELEGATION FOR API (cloudflare)
resource "aws_route53_zone" "cf-ecowater" {
  name = var.cf-sub-domain[terraform.workspace]
}

resource "aws_route53_record" "cf-ecowater" {
  allow_overwrite = true
  name            = var.cf-sub-domain[terraform.workspace]
  ttl             = 172800
  type            = "NS"
  zone_id         = aws_route53_zone.cf-ecowater.zone_id

  records = [
    aws_route53_zone.cf-ecowater.name_servers[0],
    aws_route53_zone.cf-ecowater.name_servers[1],
    aws_route53_zone.cf-ecowater.name_servers[2],
    aws_route53_zone.cf-ecowater.name_servers[3],
  ]
}


#ACM PUBLIC CERTIFICATE
resource "aws_acm_certificate" "api-ecowater_cert" {
  domain_name       = "*.${var.sub-domain[terraform.workspace]}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "api-ecowater_dv" {
  for_each = {
    for dvo in aws_acm_certificate.api-ecowater_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.api-ecowater.zone_id
}

#resource "aws_acm_certificate_validation" "api-ecowater_dv" {
#  certificate_arn         = aws_acm_certificate.api-ecowater_cert.arn
#  validation_record_fqdns = [for record in aws_route53_record.api-ecowater_dv : record.fqdn]
#}
