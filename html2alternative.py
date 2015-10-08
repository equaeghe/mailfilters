#!/usr/bin/env python3.4

"""
  html2alternative.py: A script that takes as stdin-input an rfc822 compliant
  message with a 'text/html' part (and no 'multipart/alternative' part) and
  gives as stdout-output the same message, but with both the original
  'text/html' and a new 'text/plain' part encapsulated in a
  'multipart/alternative' part.

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
import email, email.mime.text, email.mime.multipart
import html2text

# Check whether no arguments have been given to the script (it takes none)
nargs = len(sys.argv)
if len(sys.argv) is not 1:
  raise SyntaxError("This script takes no arguments, you gave " + nargs - 1 + ".")

# Read and parse the message from stdin
msg = email.message_from_bytes(sys.stdin.buffer.read())

# Build the list of 'text/html' parts in the message
htmls = []
for part in msg.walk():
  content_type = part.get_content_type()
  if content_type == 'multipart/alternative':
    raise ValueError("Message containts a 'multipart/alternative' part.")
  if content_type == 'text/html':
    htmls.append(part)

# Check that there is only a single 'text/html' part in the message
if len(htmls) is not 1:
  raise ValueError("Message does not contain exactly one 'text/html' part.")

html_old = htmls[0] # the message's single 'text/html' part

# Obtain the actual html string and generate the 'text/html' part
html_text = html_old.get_payload(decode=True).decode()
html_new = email.mime.text.MIMEText(html_text, 'html')

# Generate the 'text/plain' part
plain_text = html2text.html2text(html_text)
plain = email.mime.text.MIMEText(plain_text)

# Create the 'multipart/alternative' part
alt = email.mime.multipart.MIMEMultipart('alternative', None, [plain, html_new])

# Replace the 'text/html' part by the 'multipart/alternative' part
html_old.set_payload(alt.get_payload())
html_old.replace_header('Content-Type', alt['Content-Type'])
del html_old['Content-Transfer-Encoding']

# Check whether no errors were found in the message (parts)
if (len(msg.defects) + len(html_old.defects) + len(plain.defects)
                     + len(html_new.defects) + len(alt.defects)) > 0:
  raise Exception("An error occurred.")

# Send the modified message to stdout
print(str(msg))
