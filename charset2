#!/usr/bin/env python3

"""
charset2.py: A script that takes as stdin-input an rfc822 compliant message
that gives as stdout-output the same message, but with the charset replaced
by the target charset. Which charset is used is given by the script's
single argument: 'ansinew', 'utf8', '…'.

Copyright (C) 2026 Erik Quaeghebeur

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import email
import email.policy
import sys

CHARSETS = {
    "utf8": "utf-8",
    "ansinew": "windows-1252",
}

parser = argparse.ArgumentParser(
    description="Replace the charset used in a message's text parts."
)
parser.add_argument(
    "charset", choices=CHARSETS.keys(), help="which charset to switch to"
)
args = parser.parse_args()
charset = CHARSETS[args.charset]

# define email policy
email_policy = email.policy.EmailPolicy(
    max_line_length=None, linesep="\r\n", refold_source="none"
)

# Read and parse the message from stdin
msg = email.message_from_bytes(sys.stdin.buffer.read(), policy=email_policy)

# Replace charset string in Content-Type header
for part in msg.walk():
    if part.get_content_type() in {"text/plain", "text/html"}:
        part.set_charset(charset)

# Check whether no errors were found in the message (parts)
if len(msg.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
sys.stdout.buffer.write(msg.as_bytes(policy=email_policy))
