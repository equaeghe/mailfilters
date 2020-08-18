#!/usr/bin/env python3

"""
  multipart_get_part.py: A script that takes as stdin-input an rfc822 compliant
  multipart message and gives as stdout-output the same message, but with the
  multipart replaced by the selected child subpart. Which subpart is selected
  depends on the (symlink) name with which this script is called: its last
  character must be a (zero-indexed) number in 0-9. The corresponding child
  subpart is selected.

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

# Determine which part is selected
scriptname = sys.argv[0]
selected = int(scriptname[-1])

# define email policy
email_policy = email.policy.EmailPolicy(
  max_line_length=None, linesep="\r\n", refold_source='none')

# Read and parse the message from stdin
msg = email.message_from_bytes(sys.stdin.buffer.read(), policy=email_policy)

# Check whether the message is multipart
if not msg.is_multipart():
    raise ValueError("Message is not multipart.")

# extract the selected subpart
for k, subpart in enumerate(msg.iter_parts()):
    if k == selected:
        break

# replace the multipart by the selected subpart
msg.clear_content()
for header, value in subpart.items():
    if header in msg:
        msg.replace_header(header, value)
    else:
        msg.add_header(header, value)
msg.set_payload(subpart.get_payload(), subpart.get_content_charset())

# Check whether no errors were found in the message (parts)
if len(msg.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
sys.stdout.buffer.write(msg.as_bytes(policy=email_policy))
