#!/usr/bin/env python3

"""
  html2alternative.py: A script that takes as stdin-input an rfc822 compliant
  message with a 'text/html' part and gives as stdout-output the same message,
  but with both the first 'text/html' and a new 'text/plain' part
  encapsulated in a 'multipart/alternative' part.

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
import html2text

# Check whether no arguments have been given to the script (it takes none)
nargs = len(sys.argv)
if len(sys.argv) != 1:
    raise SyntaxError(f"This script takes no arguments, you gave {nargs - 1}.")

# define email policy
email_policy = email.policy.EmailPolicy(
  max_line_length=None, linesep="\r\n", refold_source='none')

# Read and parse the message from stdin
msg = email.message_from_bytes(sys.stdin.buffer.read(), policy=email_policy)

# Find the first 'text/html' part
replaceable = None
for part in msg.walk():
    content_type = part.get_content_type()
    if content_type == 'text/html':
        replaceable = part
        break

# Check that there is a 'text/html' part
if not replaceable:
    raise ValueError("Message does not contain a 'text/html' part.")

# Generate the 'text/plain' part
parser = html2text.HTML2Text()
parser.body_width = 0
parser.single_line_break = True
parser.unicode_snob = True
parser.inline_links = False
parser.open_quote = '“'
parser.close_quote = '”'
parser.emphasis_mark = '/'
parser.strong_mark = '*'
parser.images_to_alt = True
parser.ignore_tables = True
plain = parser.handle(replaceable.get_content())
plain = plain.replace('&amp;', '&')
# html2text apparently doesn't convert &amp; to &, so we do it
# there may be other things like this…

# replace the html part by the 'multipart/alternative'
replaceable.add_alternative(plain, cte='8bit')

# Check whether no errors were found in the message (parts)
if len(msg.defects) + len(replaceable.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
sys.stdout.buffer.write(msg.as_bytes(policy=email_policy))
