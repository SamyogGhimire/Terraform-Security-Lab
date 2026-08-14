variable "env_fqdn" {
  description = "The fqdn that will be prepended.  Current naming pattern is [dev|qa|prod].cd.code42.com"
}

resource "aws_iam_role" "s3-ro" {
  name = "terraform.${var.env_fqdn}-s3-ro"
  path = "/"
  assume_role_policy = "${data.template_file.s3-principal.rendered}"
}

resource "aws_iam_role" "s3-rw" {
  name = "terraform.${var.env_fqdn}-s3-rw"
  path = "/"
  assume_role_policy = "${data.template_file.s3-principal.rendered}"
}

resource "aws_iam_policy" "s3-ro" {
  name = "terraform.${var.env_fqdn}-s3-ro"
  policy = "${data.template_file.s3-ro.rendered}"
}

resource "aws_iam_policy" "s3-rw" {
  name = "terraform.${var.env_fqdn}-s3-rw"
  policy = "${data.template_file.s3-rw.rendered}"
}

resource "aws_iam_role_policy_attachment" "s3-ro" {
  role = "${aws_iam_role.s3-ro.name}"
  policy_arn = "${aws_iam_policy.s3-ro.arn}"
}

resource "aws_iam_role_policy_attachment" "s3-rw" {
  role = "${aws_iam_role.s3-rw.name}"
  policy_arn = "${aws_iam_policy.s3-rw.arn}"
}
