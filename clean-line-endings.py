#!/usr/bin/env python3

"""
  clean-line-endings.py: A script that takes as stdin-input an rfc822 compliant
  message that gives as stdout-output the same message, but in text/plain
  parts cleans spurious spaces in line endings.

  Copyright (C) 2024 Erik Quaeghebeur

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
import re


# Check whether no arguments have been given to the script (it takes none)
nargs = len(sys.argv)
if len(sys.argv) != 1:
    raise SyntaxError(f"This script takes no arguments, you gave {nargs - 1}.")

# define email policy
email_policy = email.policy.EmailPolicy(
  max_line_length=None, linesep="\r\n", refold_source='none')

# Read and parse the message from stdin
msg = email.message_from_bytes(sys.stdin.buffer.read(), policy=email_policy)

# Prepare regexps
spaces_at_line_end = re.compile(r"(?<!--|.:)[  ]+(?=\n)")

# Clean line endings
for part in msg.walk():
    if part.get_content_type() == 'text/plain':
        if part['Content-Type'].params.get('format') != "flowed":
          text = part.get_content()
          text = spaces_at_line_end.sub('', text)
          part.set_content(text, cte='8bit')

# Check whether no errors were found in the message (parts)
if len(msg.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
sys.stdout.buffer.write(msg.as_bytes(policy=email_policy))
