#!/usr/bin/env python3.4

"""
  clean-text-links.py: A script that takes as stdin-input an rfc822 compliant
  message that gives as stdout-output the same message, but in text/plain parts
  with fragments of the form foobar<mailto:foobar> replaced by foobar and
  foobar<http(s)://foobar> replaced by http(s)://foobar.

  Copyright (C) 2015 Erik Quaeghebeur

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
import re

# Check whether no arguments have been given to the script (it takes none)
nargs = len(sys.argv)
if len(sys.argv) is not 1:
  raise SyntaxError("This script takes no arguments, you gave " + nargs - 1 + ".")

# Read and parse the message from stdin
msg = email.message_from_bytes(sys.stdin.buffer.read())

# Prepare regexps
plain = re.compile(rb'([^<>]*)<(\1)/?>')
href = re.compile(rb'([^<>]*)<(http(s?)://\1)/?>')
mailto = re.compile(rb'([^<>]*)<mailto:(\1)>')

# Clean up link fragments
for part in msg.walk():
  if part.get_content_type() == 'text/plain':
    text = part.get_payload(decode=True)
    text = plain.sub(rb'\2', text)
    text = href.sub(rb'\2', text)
    text = mailto.sub(rb'\2', text)
    part.set_payload(text)

# Check whether no errors were found in the message (parts)
if len(msg.defects) > 0:
  raise Exception("An error occurred.")

# Send the modified message to stdout
print(str(msg))
