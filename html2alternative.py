#!/usr/bin/env python3

"""
  html2alternative.py: A script that takes as stdin-input an rfc822 compliant
  message with a 'text/html' part and gives as stdout-output the same message,
  but with both the first 'text/html' and a new 'text/plain' part
  encapsulated in a 'multipart/alternative' part.

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
import bs4
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
html = replaceable.get_content()

# # Prepare whitespace to shift whitespace out of tags
# surrounding_whitespace = re.compile(r"(\s*)(.*)(\s*)")
# 
# # Apply some fixes to html before converting to text
# soup = bs4.BeautifulSoup(html, "html5lib")
# 
# for tagtype in {"i", "b", "em", "strong"}:
#     for match in soup(tagtype):
#         parts = surrounding_whitespace.fullmatch(match.string)
#         tag = soup.new_tag(tagtype)
#         tag.string = parts[2]
#         match.replace_with(parts[1], tag, parts[3])
# 
# for match in soup("a"):
#     href = match["href"]
#     print(href)
#     text = match.string
#     if text is None:
#         # We avoid processing in case the content of the anchor is complex
#         continue
#     parts = surrounding_whitespace.fullmatch(text)
#     if href.endswith(parts[2]):
#         if href.startswith("mailto:"):
#             match.replace_with(parts[1], parts[2], parts[3])
#         else:
#             match.replace_with(parts[1], href, parts[3])
#     else:
#         tag = soup.new_tag("a")
#         tag["href"] = href
#         tag.string = parts[2]
#         match.replace_with(parts[1], tag, parts[3])
# 
# html = str(soup)

# Generate the 'text/plain' part
parser = html2text.HTML2Text()
parser.body_width = 0
parser.links_each_paragraph = True
#parser.single_line_break = True
parser.unicode_snob = True
parser.inline_links = False
parser.open_quote = '“'
parser.close_quote = '”'
parser.emphasis_mark = '/'
parser.strong_mark = '*'
parser.images_to_alt = True
parser.ignore_tables = True
parser.use_automatic_links = True
plain = parser.handle(html)
# html2text apparently doesn't convert &amp; to &, so we do it
plain = plain.replace('&amp;', '&')
# html2text incorrectly escapes dashes and periods sometimes (\-, \.),
# so we undo this, at the risk of removing true occurrences
plain = plain.replace(r'\-', '-')
plain = plain.replace(r'\.', '.')
# there may be other things like this…

# prepare cleanup regexps for common issues after conversion
nbsp = re.compile(r'\n{2}[*/]? [*/]?(?=\n)')
spaces = re.compile(r'\n{2}  \n{3}')
quote_nbsp = re.compile(r'(\n>+ ){2}[*/]? [*/]?(?=\n)')
quote_spaces = re.compile(r'(\n>+ ){2}  \1{3}')

# do cleanup using the regexps
plain = nbsp.sub(r'\n', plain)
plain = spaces.sub(r'\n', plain)
plain = quote_nbsp.sub(r'\1', plain)
plain = quote_spaces.sub(r'\1', plain)

# replace the html part by the 'multipart/alternative'
replaceable.add_alternative(plain, cte='8bit')

# Check whether no errors were found in the message (parts)
if len(msg.defects) + len(replaceable.defects) > 0:
    raise Exception("An error occurred.")

# Send the modified message to stdout
sys.stdout.buffer.write(msg.as_bytes(policy=email_policy))
