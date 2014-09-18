#!/usr/bin/env python

# This file is part of the bitbucket to github migration script.
#
# The script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the bitbucket issue migration script.
# If not, see <http://www.gnu.org/licenses/>.

from pygithub3 import Github
from datetime import datetime, timedelta
import urllib2
import time
import getpass
import sys

try:
    import json
except ImportError:
    import simplejson as json


def load_config(filename):
    json_data = open(filename)
    return json.loads(json_data)

def projects_fetch_repos():
    print "List bitbucket projects and ...\n"

def projects_rename_users():
    print "Renaming users...\n"

print "Bitbucket to Github - migration tool - v0.8"

confg_file = raw_input("Fullpath to config file : ")

# first backup all files


for dirname, dirnames, filenames in os.walk('.'):
    # print path to all subdirectories first.
    for subdirname in dirnames:
        print os.path.join(dirname, subdirname)

    # print path to all filenames.
    for filename in filenames:
        print os.path.join(dirname, filename)

    # Advanced usage:
    # editing the 'dirnames' list will stop os.walk() from recursing into there.
    if '.git' in dirnames:
        # don't go into any .git directories.
        dirnames.remove('.git')

