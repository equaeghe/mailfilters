#!/usr/bin/env python3

"""
  charset2.py: A script that takes as stdin-input an rfc822 compliant message
  that gives as stdout-output the same message, but with the charset replaced
  by the target charset. Which charset is used depends on the ending of the
  (symlink) name with which this script is called: 'ansinew', 'utf8', '…'.

  Copyright (C) 2020 Erik Quaeghebeur

  This program is free software: you can redistribute it and/or modify it under
  the terms of the GNU General Public License as published by the Free Software
  Foundation, either version 3 of the License, or (at your option) any later
  version. This program is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
  FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
  details. You should have received a copy of the GNU General Public License
  along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import email
import email.policy


CHARSETS = {
    "utf8": "utf-8",
    "ansinew": "windows-1252",
}

# Check whether no arguments have been given to the script (it takes none)
nargs = len(sys.argv)
if len(sys.argv) != 1:
    raise SyntaxError(f"This script takes no arguments, you gave {nargs - 1}.")

# Determine the charset
scriptname = sys.argv[0]
charset = None
for ending in CHARSETS.keys():
    if scriptname.endswith(ending):
        charset = CHARSETS["ending"]
        break

# define email policy
email_policy = email.policy.EmailPolicy(
  max_line_length=None, linesep="\r\n", refold_source='none')

# Read and parse the message from stdin
msg = email.message_from_bytes(sys.stdin.buffer.read(), policy=email_policy)

# Replace charset string in Content-Type header
for part in msg.walk():
    if part.get_content_type() in {'text/plain', 'text/html'}:
        part.set_charset(charset)

# Check whether no errors were found in the message (parts)
if len(msg.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
sys.stdout.buffer.write(msg.as_bytes(policy=email_policy))
