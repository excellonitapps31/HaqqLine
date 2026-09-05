#!/usr/bin/env python3
"""Reinstall the HaqqLine Let's Encrypt cert into cPanel. Runs on the sandbox host."""
from __future__ import print_function

import json
import os
import subprocess
import sys

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

DOMAIN = "haqqline.excellonit.net"
BASE = os.path.expanduser("~/.acme.sh/{0}_ecc".format(DOMAIN))


def read(name):
    path = os.path.join(BASE, name)
    with open(path, "r") as handle:
        return handle.read()


def main():
    cert = read("{0}.cer".format(DOMAIN))
    key = read("{0}.key".format(DOMAIN))
    ca = read("ca.cer")
    cmd = [
        "uapi",
        "--output=json",
        "SSL",
        "install_ssl",
        "domain={0}".format(DOMAIN),
        "cert={0}".format(quote(cert)),
        "key={0}".format(quote(key)),
        "cabundle={0}".format(quote(ca)),
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        sys.stderr.write("uapi failed\n")
        sys.exit(proc.returncode)
    payload = json.loads(out.decode("utf-8"))
    status = payload.get("result", {}).get("status")
    print("install_ssl status", status)
    if status != 1:
        sys.exit(1)


if __name__ == "__main__":
    main()
