#!/usr/bin/env python3

"""
  alternative2.py: A script that takes as stdin-input an rfc822 compliant
  message with a 'multipart/alternative' part with 'text/<target>' or
  'multipart/<target>' and/or other parts and gives as stdout-output the same
  message, but with the first 'multipart/alternative' part replaced by the
  first such target part. Which part will be output depends on the ending of
  the (symlink) name with which this script is called: 'plain', 'html',
  'calendar', 'related', or 'mixed'.

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


ALT = 'multipart/alternative'
REL = 'multipart/related'

# Check whether no arguments have been given to the script (it takes none)
nargs = len(sys.argv)
if len(sys.argv) != 1:
    raise SyntaxError(f"This script takes no arguments, you gave {nargs - 1}.")

# Determine which text part should be used
scriptname = sys.argv[0]
target = None
for ending in {'plain', 'html', 'calendar'}:
    if scriptname.endswith(ending):
        target = "text/" + ending
for ending in {'related', 'mixed'}:
    if scriptname.endswith(ending):
        target = "multipart/" + ending
if not target:
    raise ValueError(f"Unknown scriptname '{scriptname}' requested.")

# define email policy
email_policy = email.policy.EmailPolicy(
  max_line_length=None, linesep="\r\n", refold_source='none')

# Read and parse the message from stdin
msg = email.message_from_bytes(sys.stdin.buffer.read(), policy=email_policy)

# Check whether the message is multipart
if not msg.is_multipart():
    raise ValueError("Message is not multipart.")

# Find the first 'multipart/alternative' part in the message
# Also keep track of whether it is part of a multipart/related part
alt = None
container = msg
fix_main_content_type = False
for part in msg.walk():
    if (part.get_content_type() == REL) and (part.get_param('type') == ALT):
        container = part
        fix_main_content_type = True
        break
for part in container.walk():
    if (part.get_content_type() == ALT):
        alt = part
        break

# Check that there is a 'multipart/alternative' part in the message
if not alt:
    raise ValueError(f"Message does not contain a '{ALT}' part.")

# Replace the 'multipart/alternative' part by the first target part
target_missing = True
for part in alt.iter_parts():
    if part.get_content_type() == target:
        target_missing = False
        alt.clear_content()
        for header, value in part.items():
            if header in alt:
                alt.replace_header(header, value)
            else:
                alt.add_header(header, value)
        alt.set_payload(part.get_payload(), part.get_content_charset())
        break

# Bail out in case the target was not found
if target_missing:
    raise ValueError(f"Message does not contain the target part ‘{target}’.")

# As necessary, fix the 'multipart/related' part
if fix_main_content_type:
    container.set_param('type', target)

# Check whether no errors were found in the message (parts)
if len(msg.defects) + len(container.defects) + len(alt.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
sys.stdout.buffer.write(msg.as_bytes(policy=email_policy))
