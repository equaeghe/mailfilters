#!/usr/bin/env python3

"""
  alternative2.py: A script that takes as stdin-input an rfc822 compliant
  message with a 'multipart/alternative' part with 'text/<target>' or
  'multipart/<target>' and/or other parts and gives as stdout-output the same
  message, but with the 'multipart/alternative' part replaced by the target
  part. Which part will be output depends on the (symlink) name with which this
  script is called: if this name ends in 'plain', 'html', 'calendar',
  'related', or 'mixed'  the (first) such part is used.

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


ALTERNATIVE = 'multipart/alternative'
RELATED = 'multipart/related'

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

# Read and parse the message from stdin
msg = email.message_from_bytes(sys.stdin.buffer.read())

# Check whether the message contains parts
if not msg.is_multipart():
    raise ValueError("Message does not contain any subparts.")

# Build the list of 'multipart/alternative' parts in the message
# Also keep track of whether it is the root part of a multipart/related part
fix_main_content_type = False
rels = []
alts = []
for part in msg.walk():
    content_type = part.get_content_type()
    if (content_type == RELATED and part.get_param('type') == ALTERNATIVE):
        rels.append(part)
        fix_main_content_type = True
    if (content_type == ALTERNATIVE):
        alts.append(part)

# Check that there is at most one 'multipart/related' part in the message
if len(rels) > 1:
    raise ValueError("Message does not contain at most "
                     f"one '{RELATED}' part.")

# Check that there is only a single 'multipart/alternative' part in the message
if len(alts) != 1:
    raise ValueError("Message does not contain exactly "
                     f"one '{ALTERNATIVE}' part.")

if fix_main_content_type:
    rel = rels[0]  # the message's single 'multipart/related' part
alt = alts[0]  # the message's single 'multipart/alternative' part

# Obtain the constituent subparts of the single 'multipart/alternative' part
parts = alt.get_payload()

# Check whether the 'multipart/alternative' part contains the target part
if target not in {part.get_content_type() for part in parts}:
    raise ValueError("Message does not contain the target part.")

# Remove material outside of the so-called 'MIME-harness'
# of the single 'multipart/alternative' part
alt.preamble = ''
alt.epilogue = ''

# Replace the 'multipart/alternative' part by the *first* target part
for part in parts:
    if part.get_content_type() == target:
        for header, value in part.items():
            del alt[header]
            alt[header] = value
        alt.set_payload(part.get_payload())
        # replace(?) by
        #
        #   alt.set_payload(part.get_payload(), part.get_content_charset())
        #
        # to avoid the line below and current charset issues?
        #
        # Perhaps `print(str(msg))` will need to be modified
        #
        #   print(msg.as_bytes().decode(encoding=charset))
        #
        # where `charset = part.get_content_charset()` earlier.
        #
        if target.startswith('text'):
            alt.set_charset(email.charset.Charset('utf-8'))
        break  # makes sure only the first part is used

# As necessary, fix the 'multipart/related' part
if fix_main_content_type:
    rel.set_param('type', target)

# Check whether no errors were found in the message (parts)
if len(msg.defects) + len(alt.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
print(str(msg))
