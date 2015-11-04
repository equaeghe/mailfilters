#!/usr/bin/env python3.4

"""
  stdin-editor-stdout.py: A script that takes reads stdin into a temporary
  file, opens it in the program specified as an argument, outputs the edited
  file contents to stdout, and finally deletes the temporary file.

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

import tempfile
import sys
import subprocess
import os

f = tempfile.NamedTemporaryFile(delete=False)
f.write(sys.stdin.buffer.read())
filename = f.name
f.close()
subprocess.call(sys.argv[1:] + [filename])
with open(filename) as f:
  print(f.read())
os.remove(filename)
