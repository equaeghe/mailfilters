#!/usr/bin/env python3.4

"""
  to7or8bit.py: A script that takes as stdin-input an rfc822 compliant message
  with parts that are encoded as 'quoted-printable' or 'base64' and gives as
  stdout-output the same message, but with those parts replaced by either
  '7bit' or '8bit' transformations of themselves.

  Copyright (C) 2014 Erik Quaeghebeur

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

# Check whether no arguments have been given to the script (it takes none)
nargs = len(sys.argv)
if len(sys.argv) is not 1:
  raise SyntaxError("This script takes no arguments, you gave " + nargs - 1 + ".")

# Read and parse the message from stdin
msg = email.message_from_string(sys.stdin.read())

# Transform 'quoted-printable' and 'base64' to '7bit' or '8bit'
for part in msg.walk():
  if part.get_content_maintype() == 'text':
    if part['Content-Transfer-Encoding'] in {'quoted-printable', 'base64'}:
      payload = part.get_payload(decode=True)
      del part['Content-Transfer-Encoding']
      part.set_payload(payload)
      email.encoders.encode_7or8bit(part)

# Check whether no errors were found in the message (parts)
if len(msg.defects) > 0:
  raise Exception("An error occurred.")

# Send the modified message to stdout
print(msg.as_bytes().decode(encoding='UTF-8'))
