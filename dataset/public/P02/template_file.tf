data "template_file" "s3-ro" {
  template = "${file("${path.module}/policy.s3-ro.tpl")}"
  vars {
    bucket_name= "terraform.${var.env_fqdn}"
  }
}


data "template_file" "s3-rw" {
  template = "${file("${path.module}/policy.s3-rw.tpl")}"
  vars {
    bucket_name= "terraform.${var.env_fqdn}"
  }
}

data "template_file" "s3-principal" {
  template = "${file("${path.module}/policy.s3-principal.tpl")}"
  vars {
    bucket_name= "terraform.${var.env_fqdn}"
  }
}
