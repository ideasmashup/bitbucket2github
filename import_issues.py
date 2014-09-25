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
    'date' : datetime.date.today()
    
}

COLOR_COMPONENT = "339999"
COLOR_VERSION = "eeeeee"
COLOR_REPOS   = "dddddd"

count = 0;

github_data = None
bitbucket_data = None

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
# -------------------------------------------------------------
if options.verbose:
    print 'Loading issues from: ' + options.json_file

json_str = open(options.json_file).read()
bitbucket_data = json.loads(json_str)

if options.verbose:
    pprint(bitbucket_data)
# -------------------------------------------------------------



# fetch default values
# -------------------------------------------------------------
def import_metas(metas):
    if options.verbose:
        print 'Importing '+ `len(metas)` +' default value(s)...'
    
    count = 0
    for key, value in metas.items():
        if key is not None and value is not None:
            count += 1
            print '- importing #'+ `count` 
            if options.verbose:
                print '- default '+ key.decode('utf-8') +' = '+ value.decode('utf-8') 
            if not options.dry_run:
                DEFAULTS[key.decode('utf-8')] = value.decode('utf-8')
    
    print 'Done importing default values.'

# defaults from meta fields
metas = bitbucket_data['meta']
import_metas(metas)

if options.verbose:
    print 'Setting default date to: ' + DEFAULTS['date'].strftime("%Y-%m-%dT%H:%M:%SZ")
# -------------------------------------------------------------



# copy all milestones
# -------------------------------------------------------------
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

def import_milestones(milestones):
    github_milestones = {}
    
    if options.verbose:
        print 'Importing '+ `len(milestones)` +' milestone(s)...'

    count = 0;
    for milestone in milestones:
        count += 1
        print '- importing #'+ `count`
        if options.verbose:
            print '- creating new "' + milestone['name'] + '" milestone with no description and deadline set to ('+ DEFAULTS['date'].strftime("%Y-%m-%dT%H:%M:%SZ") +')'
        if not options.dry_run:
            try: 
                github_milestones[milestone['name']] = r.create_milestone(milestone['name'], "open", "", datetime.date.today())
            except Exception:
                # ignore exceptions and attempt to import next entry
                sys.exc_clear()

    print 'Done importing milestones.'
    return github_milestones

github_data['milestones'] = import_milestones(bitbucket_data['milestones'])
# -------------------------------------------------------------



# create label for repository (for multi-repos merges?)
# -------------------------------------------------------------
if options.verbose:
    print '- creating new label "' + options.repository + '"'
if not options.dry_run:
    r.create_label(options.repository, COLOR_REPOS)
# -------------------------------------------------------------



# copy versions as labels
# -------------------------------------------------------------
#
# "versions":[
#   {
#      "name":"Interne 0"
#   },
#   {
#      "name":"Interne 1"
#   },
#   {
#      "name":"Interne 2"
#   },
# ],

versions = bitbucket_data['versions']
if options.verbose:
    print 'Importing '+ `len(versions)` +' versions(s)...'

count = 0
for version in versions:
    count += 1
    print '- importing #'+ `count`
    if options.verbose:
        print '- creating new label "' + version['name'] + '"'
    if not options.dry_run:
        r.create_label(version['name'], COLOR_VERSION)

if options.verbose:
    print 'Done importing versions.'
# -------------------------------------------------------------



# copy components as labels
# -------------------------------------------------------------
#
# "components":[
#    {
#       "name":"Configuration"
#    },
#    {
#       "name":"Effets speciaux"
#    },
#    {
#       "name":"Fonctions vocales"
#    },
#    {
#        "name":"Intelligence"
#    },
#    {
#       "name":"Interface utilisateur"
#    },
#    {
#       "name":"Internet"
#    },
# ],

components = bitbucket_data['components']
if options.verbose:
    print 'Importing '+ `len(components)` +' component(s)...'

count = 0
for component in components:
    count += 1
    print '- importing #'+ `count`
    if options.verbose:
        print '- creating new label "' + component['name'] + '"'
    if not options.dry_run:
        r.create_label(component['name'], COLOR_COMPONENT)

if options.verbose:
    print 'Done importing components.'
# -------------------------------------------------------------



# attachemnts (ignored - not implemented yet)
# -------------------------------------------------------------
# 
# "attachments":[
#       // no sample data in our projects
# ],

attachments = bitbucket_data['attachments']
if options.verbose:
    print 'Importing '+ `len(attachments)` +' attachments(s)...'

print 'ERROR: NOT IMPLEMENTED YET... attachments ignored!'

if options.verbose:
    print 'Done importing attachments.'
# -------------------------------------------------------------



# copy all issues
# -------------------------------------------------------------
# 
# "issues":[
#     {
#        "status":"new",
#        "priority":"major",
#        "kind":"task",
#        "content_updated_on":null,
#        "voters":[
#     
#        ],
#        "title":"Mission 2 : deplacement du robot",
#        "reporter":"probeability",
#        "component":null,
#        "watchers":[
#           "MahmoudLH",
#           "probeability"
#        ],
#        "content":"# Objectifs de la mission\r\n\r\n1. le robot peut se deplacer dans toutes les directions\r\n2. le robot peut detecter et contourner des obstacles\r\n3. le robot peut se reperer dans l'espace (ou au minimum suivre un trajet predefini - sans marquage au sol)\r\n\r\n*Actuellement on peut commander certains deplacements du robot, il n'est pas autonome car il n'utilise pas la sonde ultrason, il est aveugle et aussi les moteurs sont \"brushless\" donc tres imprecis*\r\n\r\n# Ameliorations\r\n\r\n- utiliser le sonar pour detecter des obstacles qui ne sont pas au niveau du sol\r\n    - identifier si c'est un obstacle immobile ou autre (une personne qui bouge)\r\n    - attendre et reprendre le deplacement initial ou changer de route pour le contourner\r\n- utiliser le gyroscope android pour obtenir des informations directionnelles (compas, orientation, etc)\r\n- permettre d'enregistrer des deplacements predefinis et de les reproduire en boucle\r\n    - par exemple en enregistrant les appuis sur les boutons fleches du smartphone dans un fichier (par exemple faire bouger le robot dans le bureau de Zarzis et revenir a son point de depart)\r\n    - ensuite permettre de charger les deplacements depuis le fichier pour que le robot recommence tout seul\r\n    - le fichier doit etre editable avec un editeur texte pour faciliter le debug\r\n- quand Marouane aura remplace les moteur \"brushless\" par des \"pas-a-pas continus\" (plus precis)\r\n    - ameliorer la precision des deplacements (ie. rotation des roues precise en radians, nb de tours, duree, vitesse, etc)\r\n    - rendre les deplacements plus \"doux\" (easing)\r\n\r\n# A faire\r\n\r\n- reprendre le code de Mahmoud, discuter avec lui + Marouane pour avoir un etat des lieux\r\n- estimer ce qui peut avancer sur cette mission d'ici le 30 septembre",
#        "assignee":"MahmoudLH",
#        "created_on":"2014-09-01T03:56:21.849373+00:00",
#        "version":"Interne 3",
#        "edited_on":null,
#        "milestone":"Prototypage interne",
#        "updated_on":"2014-09-01T03:56:21.849373+00:00",
#        "id":50
#     },
# ],

def issue_content(issue):
    content = "*original issue: *" # add all missing details after import here
    content += issue['content']
    return content

issues = bitbucket_data['issues']
print 'Start importing '+ `len(issues)` +' issues(s)...'

count = 0
for issue in issues:
    count += 1
    print '- importing #'+ `count`
    if options.verbose:
        print '- creating new issue "' + issue['content'] + '"'
    if not options.dry_run:
        labels = []
        r.create_issue(issue['title'], issue_content(issue), issue['assignee'], milestone, labels)

print 'Done importing issues.'
# -------------------------------------------------------------



# copy all comments
# -------------------------------------------------------------
# 
# "comments":[
#   {
#      "content":"je suis entrain d'integrer la fonction \"face-detection\" dans notre app",
#      "created_on":"2014-08-13T10:55:50.397164+00:00",
#      "user":"MahmoudLH",
#      "updated_on":null,
#      "issue":47,
#      "id":11762417
#   },
#   {
#      "content":null,
#      "created_on":"2014-08-13T10:51:49.410123+00:00",
#      "user":"MahmoudLH",
#      "updated_on":null,
#      "issue":46,
#      "id":11761742
#   },
# ],

comments = bitbucket_data['comments']
print 'Start importing '+ `len(comments)` +' comment(s)...'

count = 0
for comment in comments:
    count += 1
    print '- importing #'+ `count`
    if options.verbose:
        print '- creating new comment "' + comment['content'] + '"'
    if not options.dry_run:
        r.create_comment(comment['content'])

print 'Done importing comments.'
# -------------------------------------------------------------


# copy all logs
# -------------------------------------------------------------
# 
# "logs":[
#   {
#      "comment":9500004,
#      "changed_to":"Prototypage interne",
#      "field":"milestone",
#      "created_on":"2014-04-05T04:47:20.549697+00:00",
#      "user":"probeability",
#      "issue":20,
#      "changed_from":"Alpha"
#   },
#   {
#      "comment":11271837,
#      "changed_to":"resolved",
#      "field":"status",
#      "created_on":"2014-07-16T14:51:55.107022+00:00",
#      "user":"MahmoudLH",
#      "issue":25,
#      "changed_from":"new"
#   }
# ],

logs = bitbucket_data['logs']
print 'Start importing '+ `len(logs)` +' log(s)...'


for log in logs:
    if options.verbose:
        print '- creating new log "' + log['content'] + '"'
#     if not options.dry_run:
#         r.create_issue(title, comment['content'], assignee, milestone, labels)

print 'Done importing logs.'
# -------------------------------------------------------------
