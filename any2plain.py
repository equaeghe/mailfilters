#!/usr/bin/env python3.4

"""
  any2plain.py: A script that takes as stdin-input an rfc822 compliant message
  with any MIME structure containing a 'text/plain' part and gives as
  stdout-output the same message, but with the whole body replaced by the first
  text/plain part.

  Copyright (C) 2016 Erik Quaeghebeur

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
msg = email.message_from_bytes(sys.stdin.buffer.read())

# Check whether the message contains parts
if not msg.is_multipart():
    raise ValueError("Message does not contain any subparts.")

# Find the first text/plain part and replace message payloads with its payload
for part in msg.walk():
    content_type = part.get_content_type()
    if (content_type == 'text/plain'):
        for header, value in part.items():
            del msg[header]
            msg[header] = value
        msg.set_payload(part.get_payload())

# Check whether no errors were found in the message (parts)
if len(msg.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
print(str(msg))
