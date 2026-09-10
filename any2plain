#!/usr/bin/env python3

"""
  any2plain.py: A script that takes as stdin-input an rfc822 compliant message
  with any MIME structure containing a 'text/plain' part and gives as
  stdout-output the same message, but with the whole body replaced by the main
  text/plain part.

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


# Check whether no arguments have been given to the script (it takes none)
nargs = len(sys.argv)
if len(sys.argv) != 1:
    raise SyntaxError(f"This script takes no arguments, you gave {nargs - 1}.")

# define email policy
email_policy = email.policy.EmailPolicy(
  max_line_length=None, linesep="\r\n", refold_source='none')

# Read and parse the message from stdin
msg = email.message_from_bytes(sys.stdin.buffer.read(), policy=email_policy)

# Check whether the message contains parts
if not msg.is_multipart():
    raise ValueError("Message does not contain any subparts.")

# Find the body 'text/plain' part and replace message content with its content
body = msg.get_body(('plain',))
msg.clear_content()
for header, value in body.items():
    if header in msg:
        msg.replace_header(header, value)
    else:
        msg.add_header(header, value)
msg.set_payload(body.get_payload(), body.get_content_charset())

# Check whether no errors were found in the message (parts)
if len(msg.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
sys.stdout.buffer.write(msg.as_bytes(policy=email_policy))
