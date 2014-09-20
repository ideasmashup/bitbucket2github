#!/usr/bin/env python

# Bitbucket to Github Migration Tools
# -----------------------------------
# Copyright (c) 2014 William ANGER
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json
import getpass
import collections
import datetime

# parse parameters and show help
from optparse import OptionParser
parser = OptionParser()

parser.add_option("-t", "--dry-run", action="store_true", dest="dry_run", default=False,
    help="Perform a dry run and print eveything.")

parser.add_option("-u", "--username", dest="github_login",
    help="Username of target GitHub account.")

parser.add_option("-r", "--repository", dest="repository",
    help="GitHub repository where to import the issues")

parser.add_option("-f", "--file", dest="json_file", default="db-1.0.json",
    help="Source JSON file containing the issues to import")

(options, args) = parser.parse_args()


# connect to GitHub API v3 
# see: https://github.com/jacquev6/PyGithub
# see: https://developer.github.com/v3/
from github import Github

print 'Please enter your github password'
github_password = getpass.getpass()
github_login = options.github_logi

g = Github(github_login, github_password)


# load target repo
r = g.get_user().get_repo(options.repository)
print 'opening GitHub repository: ' + r.name

# load issues json file
json_str = open(options.json_file) # raw_input('Issues export file in JSON format (default: db-1.0.json)
issues = json.loads(json_str, object_pairs_hook=collections.OrderedDict)

#
today = datetime.date.today()
date= today.strftime("%Y-%m-%d %H:%M") # YYYY-MM-DDTHH:MM:SSZ

# 
for milestone in issues['milestones']:
    print 'Processing: ' + milestone
    r.create_milestone(milestone.name, "open", "(auto-imported)", "2012-10-09T23:39:01Z")
