#!/usr/bin/env python3

"""
  clean-text-links.py: A script that takes as stdin-input an rfc822 compliant
  message that gives as stdout-output the same message, but in text/plain
  parts cleans up all kinds of link-related issues and html leftovers, such as
  ‘&nbsp;’.

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
import re
from urllib.parse import unquote


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
# link rewriters
outlook = re.compile(r'(?i)https://\w+.safelinks\.protection\.outlook\.com/'
                     r'[\w/-]*\?url=([^&]*)&\S*reserved=0')
proofpoint2 = re.compile(r'(?i)https://urldefense\.proofpoint\.com/v2/url\?'
                         r'u=([^=&]*)&\S*(?:(?= [^>\]\)])| ?)')
proofpoint3 = re.compile(r'(?i)https://urldefense\.com/v3/__(.*)__;[^\$]*\$')
fireeye = re.compile(r'(?i)https://protect3-qa\.fireeye\.com/v1/url\?.*'
                     r'u=([^>\s\]\)]+)')
clicktime = re.compile(r'(?i)https://[\w-]+\.trendmicro\.com(?:\:443)?/wis/'
                       r'clicktime/v1/query\?url=(.+)&umid=[\w-]+&auth=[\w-]+')
vadesecure4 = re.compile(r'(?i)https://antiphishing.vadesecure.com/v4?.*u=(.*)')
# typical doublings
href = re.compile(r'(?i)(?:https?://)?([^<>\[\]\(\)]{3,})\s*?'
                  r'[<\[\(] *?(https?://\1/?) *?[\)\]>]')
mailto = re.compile(r'(?i)([\'"]?)([^<>\[\]\(\)\'"]{3,})\1\s*?'
                    r'[<\[\(] *?(?:mailto:|sip:|tel:)?\2 *?[\)\]>]')
# warning note
exchangewarning_text = re.compile(
    r"\[?"
    r"([A-Z][\w\s'-]* \S*@\S*\. [A-Z][\w\s'-]+)\s*"
    r"(<?https://aka\.ms/LearnAboutSenderIdentification>?\s*)"
    r"\]?\n*")
exchangewarning_html = re.compile(
    r"[A-Z]{0,1}[\w\s'-]*.*@.*\. "
    r"\[\s*[A-Z][\w\s'-]+\]\[1\](?:\s*\n)+"
    r"\s*\[1\]: https://aka.ms/LearnAboutSenderIdentification\n*")
# random stuff
nbsp = re.compile(r'&nbsp;')


# Custom replacement functions

def rewriter_fix(rewriter=None):

    def fixer(match):
        link = match[1]
        if rewriter == 'proofpoint2':
            link = link.replace('_', '/').replace('-', '%')
        if rewriter == 'proofpoint3':
            link = link.replace('*', '%')
        return unquote(link)

    return fixer


# Clean up link fragments
for part in msg.walk():
    if part.get_content_type() == 'text/plain':
        text = part.get_content()
        text = exchangewarning_text.sub('', text)
        text = exchangewarning_html.sub('', text)
        text = outlook.sub(rewriter_fix(), text)
        text = proofpoint2.sub(rewriter_fix('proofpoint2'), text)
        text = proofpoint3.sub(rewriter_fix('proofpoint3'), text)
        text = fireeye.sub(rewriter_fix(), text)
        text = vadesecure4.sub(rewriter_fix(), text)
        text = clicktime.sub(rewriter_fix(), text)
        text = href.sub(r'\2', text)
        text = mailto.sub(r'\2', text)
        text = nbsp.sub(' ', text)
        part.set_content(text, cte='8bit')

# Check whether no errors were found in the message (parts)
if len(msg.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
sys.stdout.buffer.write(msg.as_bytes(policy=email_policy))
