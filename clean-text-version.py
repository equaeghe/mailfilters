#!/usr/bin/env python3

"""
  clean-text-links.py: A script that takes as stdin-input an rfc822 compliant
  message that gives as stdout-output the same message, but in text/plain parts
  with fragments of the form foobar<mailto:foobar> replaced by foobar,
  foobar<http(s)://foobar> replaced by http(s)://foobar. Also deals with with
  spaces before and after ‘<’, and ‘>’ and with ‘<>’ in replaced by ‘[]’ or
  ‘()’. Furthermore also cleans up some html leftovers, such as ‘&nbsp;’.

  Copyright (C) 2019 Erik Quaeghebeur

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
from urllib.parse import unquote_to_bytes
from quopri import encodestring


# Check whether no arguments have been given to the script (it takes none)
nargs = len(sys.argv)
if len(sys.argv) is not 1:
  raise SyntaxError("This script takes no arguments, you gave " + nargs - 1 + ".")

# Read and parse the message from stdin
msg = email.message_from_bytes(sys.stdin.buffer.read())

# Prepare regexps
# link rewriters
outlook = re.compile(rb'(?i)https://\w+.safelinks\.protection\.outlook\.com/\?url=([^&]*)&\S*reserved=0')
proofpoint = re.compile(rb'(?i)https://urldefense\.proofpoint\.com/v2/url\?u=([^=&]*)&\S*\s')
# typical doublings
href = re.compile(rb'(?i)(?:https?://)?([^<>\[\]\(\)]*)\s*?[<\[\(]\s*?(https?://\1/?)\s*?[\)\]>]')
mailto = re.compile(rb'(?i)[\'"]?([^<>\[\]\(\)\'"]*)[\'"]?\s*?[<\[\(]\s*?(?:mailto|sip|tel):\1\s*?[\)\]>]')
# random stuff
nbsp = re.compile(rb'(&nbsp;)')

# Custom replacement functions
def rewriter_fix(encoding, rewriter):
    if encoding == 'quoted-printable':
        encoder = encodestring
    else:
        encoder = lambda blob: blob
        
    def fixer(match):
        link = match[1]
        if rewriter == 'proofpoint':
            link = link.replace(b'_', b'/').replace(b'-', b'%')
        return encoder(unquote_to_bytes(link))
    
    return fixer


# Clean up link fragments
for part in msg.walk():
  if part.get_content_type() == 'text/plain':
    encoding = part['Content-Transfer-Encoding'].lower()
    text = part.get_payload(decode=True)
    text = outlook.sub(rewriter_fix(encoding, 'outlook'), text)
    text = proofpoint.sub(rewriter_fix(encoding, 'proofpoint'), text)
    text = href.sub(rb'\2', text)
    text = mailto.sub(rb'\1', text)
    text = nbsp.sub(' '.encode(), text)
    part.set_payload(text)

# Check whether no errors were found in the message (parts)
if len(msg.defects) > 0:
  raise Exception("An error occurred.")

# Send the modified message to stdout
print(str(msg))
