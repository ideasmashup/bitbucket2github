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
import datetime

# parse parameters and show help
from optparse import OptionParser
from pprint import pprint
parser = OptionParser()

parser.add_option("-t", "--dry-run", action="store_true", dest="dry_run", default=False,
    help="Perform a dry run and print eveything.")

parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
    help="Show detailed output of issues entries processing.")

parser.add_option("-u", "--username", dest="github_login",
    help="Username of target GitHub account.")

parser.add_option("-r", "--repository", dest="repository",
    help="GitHub repository where to import the issues")

parser.add_option("-f", "--file", dest="json_file", default="db-1.0.json",
    help="Source JSON file containing the issues to import")

(options, args) = parser.parse_args()

# config values
DEFAULTS = {
    # default today's date for bitbucket data that doesn't have one (milestones...)
    'date' : datetime.date.today().strftime("%Y-%m-%dT%H:%M:%SZ"), # YYYY-MM-DDTHH:MM:SSZ
}

COLOR_VERSION = "eeeeee"
COLOR_REPOS   = "dddddd"


# connect to GitHub API v3 
# see: https://github.com/jacquev6/PyGithub
# see: https://developer.github.com/v3/
from github import Github

if not options.dry_run:
    print 'Please enter your github password'
    github_password = getpass.getpass()
    github_login = options.github_login
    g = Github(github_login, github_password)

    # load target repo
    r = g.get_user().get_repo(options.repository)
    print 'Opening GitHub repository: ' + r.name


# load issues json file
if options.verbose:
    print 'Loading issues from: ' + options.json_file

json_str = open(options.json_file).read()
data = json.loads(json_str)

if options.verbose:
    pprint(data)



if options.verbose:
    print 'Setting default date to: ' + DEFAULTS['date']

# copy all milestones
"""
"milestones":[
   {
      "name":"September sprint"
   },
   {
      "name":"October sprint"
   },
   {
      "name":"Preview release"
   },
   {
      "name":"Bugsmashing marathon"
   }
],
"""
milestones = data['milestones']
if options.verbose:
    print 'Importing '+ `len(milestones)` +' milestone(s)...'

for milestone in milestones:
    if options.verbose:
        print '- creating new "' + milestone['name'] + '" milestone with no description and deadline set to ('+ DEFAULTS['date'] +')'
    if not options.dry_run:
        r.create_milestone(milestone['name'], "open", "", DEFAULTS['date'])

print 'Done importing milestones.'


# create label for repository (for multi-repos merges?)
if options.verbose:
    print '- creating new label "' + options.repository + '"'
if not options.dry_run:
    r.create_label(options.repository, COLOR_REPOS)

# copy versions as labels
"""
"versions":[
  {
     "name":"Interne 0"
  },
  {
     "name":"Interne 1"
  },
  {
     "name":"Interne 2"
  },
],
"""
versions = data['versions']
if options.verbose:
    print 'Importing '+ `len(versions)` +' versions(s)...'

for version in versions.items():
    if options.verbose:
        print '- creating new label "' + version['name'] + '"'
    if not options.dry_run:
        r.create_label(version['name'], COLOR_VERSION)

if options.verbose:
    print 'Done importing versions.'


# attachemnts (ignored - not implemented yet)
"""
"attachments":[
      // no sample data in our projects
],
"""
attachments = data['attachments']
if options.verbose:
    print 'Importing '+ `len(attachments)` +' attachments(s)...'

print 'ERROR: NOT IMPLEMENTED YET... attachments ignored!'

if options.verbose:
    print 'Done importing attachments.'


# copy all issues
"""
"issues":[
    {
       "status":"new",
       "priority":"major",
       "kind":"task",
       "content_updated_on":null,
       "voters":[
    
       ],
       "reporter":"probeability",
       "component":null,
       "watchers":[
          "MahmoudLH",
          "probeability"
       ],
       "content":"# Objectifs de la mission\r\n\r\n1. le robot peut se déplacer dans toutes les directions\r\n2. le robot peut détecter et contourner des obstacles\r\n3. le robot peut se repérer dans l'espace (ou au minimum suivre un trajet prédéfini - sans marquage au sol)\r\n\r\n*Actuellement on peut commander certains déplacements du robot, il n'est pas autonome car il n'utilise pas la sonde ultrason, il est aveugle et aussi les moteurs sont \"brushless\" donc très imprécis*\r\n\r\n# Améliorations\r\n\r\n- utiliser le sonar pour détecter des obstacles qui ne sont pas au niveau du sol\r\n    - identifier si c'est un obstacle immobile ou autre (une personne qui bouge)\r\n    - attendre et reprendre le déplacement initial ou changer de route pour le contourner\r\n- utiliser le gyroscope android pour obtenir des informations directionnelles (compas, orientation, etc)\r\n- permettre d'enregistrer des déplacements prédéfinis et de les reproduire en boucle\r\n    - par exemple en enregistrant les appuis sur les boutons flèches du smartphone dans un fichier (par exemple faire bouger le robot dans le bureau de Zarzis et revenir à son point de départ)\r\n    - ensuite permettre de charger les déplacements depuis le fichier pour que le robot recommence tout seul\r\n    - le fichier doit être éditable avec un éditeur texte pour faciliter le debug\r\n- quand Marouane aura remplacé les moteur \"brushless\" par des \"pas-à-pas continus\" (plus précis)\r\n    - améliorer la précision des déplacements (ie. rotation des roues précise en radians, nb de tours, durée, vitesse, etc)\r\n    - rendre les déplacements plus \"doux\" (easing)\r\n\r\n# A faire\r\n\r\n- reprendre le code de Mahmoud, discuter avec lui + Marouane pour avoir un état des lieux\r\n- estimer ce qui peut avancer sur cette mission d'ici le 30 septembre",
       "assignee":"MahmoudLH",
       "created_on":"2014-09-01T03:56:21.849373+00:00",
       "version":"Interne 3",
       "edited_on":null,
       "milestone":"Prototypage interne",
       "updated_on":"2014-09-01T03:56:21.849373+00:00",
       "id":50
    },
],
"""
issues = data['issues']
print 'Start importing '+ `len(issues)` +' issues(s)...'
print 'Done importing issues.'
