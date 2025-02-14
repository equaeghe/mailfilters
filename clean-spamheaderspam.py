#!/usr/bin/env python3

"""
  clean-spamheaderspam.py: A script that takes as stdin-input an rfc822
  compliant message that gives as stdout-output the same message, but many
  kinds of lengthy spam headers removed.

  Copyright (C) 2025 Erik Quaeghebeur

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

# Clean spam headers
del msg["x-forefront-antispam-report"]
del msg["X-Forefront-Antispam-Report-Untrusted"]
del msg["x-microsoft-antispam"]
del msg["X-Microsoft-Antispam-Untrusted"]
del msg["X-Microsoft-Antispam-Mailbox-Delivery"]
del msg["X-Microsoft-Antispam-Message-Info-Original"]
del msg["X-Microsoft-Antispam-Message-Info"]
del msg["x-ms-exchange-antispam-relay"]
del msg["X-MS-Exchange-AntiSpam-MessageData-Original-ChunkCount"]
del msg["X-MS-Exchange-AntiSpam-MessageData-Original-0"]

# Check whether no errors were found in the message (parts)
if len(msg.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
sys.stdout.buffer.write(msg.as_bytes(policy=email_policy))
