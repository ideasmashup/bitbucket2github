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
from github.GithubException import GithubException
parser = OptionParser()

parser.add_option("-t", "--dry-run", action="store_true", dest="dry_run", default=False,
    help="Perform a dry run and print eveything.")

parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
    help="Show detailed output of issues entries processing.")

parser.add_option("-u", "--username", dest="github_login", default=None,
    help="Username of target GitHub account.")

parser.add_option("-c", "--conf", dest="config_file", default=None,
    help="JSON config file to use for migration settings.")

parser.add_option("-r", "--repository", dest="repository",
    help="GitHub repository where to import the issues.")

parser.add_option("-f", "--file", dest="json_file", default="db-1.0.json",
    help="Source JSON file containing the issues to import.")

(options, args) = parser.parse_args()

# config values
config = None

DEFAULTS = {
    # default today's date for bitbucket data that doesn't have one (milestones...)
    'date' : datetime.date.today()
}

COLOR_COMPONENT = "ff9900"
COLOR_VERSION   = "ffcc00"
COLOR_REPOS     = "ccff00"
COLOR_KIND      = "cccc00"
COLOR_PRIORITY  = "ff6600"

count = 0
github_data = {}
bitbucket_data = {}

github_login = None
github_password = None
bitbucket_repo = None
github_merge_repo = None
github_repo = None
github_subtree = ''



if options.verbose:
    print 'BitBucket to GitHub v0.7'

def load_json(filename):
    if options.verbose:
        print 'Loading data from JSON file: ' + filename

    json_str = open(filename).read()
    data = json.loads(json_str)
    if options.verbose:
        print '- loaded ' + `len(json_str)` + ' bytes'
        # pprint(data)

    return data


# load config file
if options.config_file is not None:
    config = load_json(str(options.config_file))

# connect to GitHub API v3 
# see: https://github.com/jacquev6/PyGithub
# see: https://developer.github.com/v3/
from github import Github

if not options.dry_run:
    if config is not None and config['login']['github']['user'] is not None:
        github_login = config['login']['github']['user']
        if options.verbose:
            print '- fetching login from config file ' + github_login
    elif options.github_login is not None:
        github_login = options.github_login
        if options.verbose:
            print '- fetching login from script -u parameter value ' + github_login
    else:
        github_login = raw_input('Please enter your github login: ')

    if config is not None and config['login']['github']['pass'] is not None:
        github_password = config['login']['github']['pass']
        if options.verbose:
            print '- fetching password from config file ' + ('*' * len(github_password))[:len(github_password)]
    else:
        print 'Please enter your github password: '
        github_password = getpass.getpass()

    if options.verbose:
        print '- connecting to GitHub using: ' + github_login + ' ' + ('*' * len(github_password))[:len(github_password)]

    g = Github(github_login, github_password)

    # fetch then loop through all repos entries from the config file
    if config is not None and config.get('repos') is not None:
        bitbucket_repos = config['repos']
    else:
        bitbucket_repos = {}

    # global merge repo
    if config is not None and config.get('merge_repo') is not None:
        github_merge_repo = config['merge_repo']
        if options.verbose:
            print '- fetching merge repo from config file ' + github_merge_repo


    for bitbucket_repo_name, bitbucket_repo in bitbucket_repos.iteritems():
        if options.verbose:
            print 'Start importing repo ' + bitbucket_repo_name

        if bitbucket_repo['merge'] is False:
            github_repo = bitbucket_repo['name']
            github_subtree = ''
        elif bitbucket_repo['merge'] is True and github_merge_repo is not None:
            github_repo = github_merge_repo
            github_subtree = bitbucket_repo['name']
        else:
            github_repo = bitbucket_repo['merge']
            github_subtree = bitbucket_repo['name']

        if options.verbose:
            print '- imported as ' + github_repo + '(/' + github_subtree + ')'


        # load target repo
        r = g.get_user().get_repo(github_repo)
        print 'Opening GitHub repository: ' + r.name

        # load issues json file
        # -------------------------------------------------------------
        bitbucket_data = load_json(options.json_file)
        # -------------------------------------------------------------
        
        
        
        # fetch default values
        # -------------------------------------------------------------
        #
        # "meta":{
        #    "default_milestone":null,
        #    "default_assignee":null,
        #    "default_kind":"bug",
        #    "default_component":null,
        #    "default_version":null
        # },
        
        def import_metas(metas):
            output = {}
        
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
                        output[key.decode('utf-8')] = value.decode('utf-8')
        
            print 'Done importing default values.'
            return output
        
        # defaults from meta fields
        github_data['metas'] = import_metas(bitbucket_data['meta'])
        
        if options.verbose:
            print 'Setting default date to: ' + DEFAULTS['date'].strftime("%Y-%m-%dT%H:%M:%SZ")
        # -------------------------------------------------------------
        
        
        
        # import all milestones
        # -------------------------------------------------------------
        # 
        # "milestones":[
        #    {
        #       "name":"September sprint"
        #    },
        #    {
        #       "name":"October sprint"
        #    },
        #    {
        #       "name":"Preview release"
        #    },
        #    {
        #       "name":"Bugsmashing marathon"
        #    }
        # ],
        
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
                    except GithubException as ex:
                        print '- failed to create milestone: ' + milestone['name'] + '\n    ' + str(ex)
            print 'Done importing milestones.'
            return github_milestones
        
        
        github_data['milestones'] = import_milestones(bitbucket_data['milestones'])
        
        if options.verbose:
            print 'Imported milestones :'
            for mobj in github_data['milestones']:
                print (mobj)
        # -------------------------------------------------------------
        
        
        
        # -------------------------------------------------------------
        github_data['labels'] = {}
        def add_label(label):
            github_data['labels'][label.name] = label
        
        def create_label(repo, color):
            label = None
            if options.verbose:
                print '- creating new label "' + repo + '"'
            if not options.dry_run:
                label = r.create_label(repo, color)
                add_label(label)
        
            return label
        # -------------------------------------------------------------
        
        # create label for repository (for multi-repos merges?)
        create_label(github_repo, COLOR_REPOS)
        
        # import issues kinds and priorities as labels
        # -------------------------------------------------------------
        def import_kinds():
            # only import as labels when they don't exist already
            labels = ['proposal', 'task']
        
            if options.verbose:
                print 'Importing '+ `len(labels)` +' (s)...'
        
            count = 0
            for label in labels:
                count += 1
                print '- importing #'+ `count`
                if not options.dry_run:
                    label = create_label(label, COLOR_KIND)
            
            if options.verbose:
                print 'Done importing kinds.'
        
            return labels
        
        def import_priorities():
            labels = ['major', 'trivial', 'minor', 'critical', 'blocker']
        
            if options.verbose:
                print 'Importing '+ `len(labels)` +' (s)...'
        
            count = 0
            for label in labels:
                count += 1
                print '- importing #'+ `count`
                if not options.dry_run:
                    label = create_label(label, COLOR_PRIORITY)
            
            if options.verbose:
                print 'Done importing priorities.'
        
            return labels
        
        
        import_kinds()
        import_priorities()
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
        
        def import_versions(versions):
            labels = []
        
            if options.verbose:
                print 'Importing '+ `len(versions)` +' version(s)...'
        
            count = 0
            for version in versions:
                count += 1
                print '- importing #'+ `count`
                if not options.dry_run:
                    label = create_label(version['name'], COLOR_VERSION)
                    labels.append(label)
            
            if options.verbose:
                print 'Done importing versions.'
        
            return labels
        
        
        import_versions(bitbucket_data['versions'])
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
        def import_components(components):
            labels = []
        
            if options.verbose:
                print 'Importing '+ `len(components)` +' component(s)...'
        
            count = 0
            for component in components:
                count += 1
                print '- importing #'+ `count`
                if not options.dry_run:
                    label = create_label(component['name'], COLOR_COMPONENT)
                    labels.append(label)
        
            if options.verbose:
                print 'Done importing components.'
        
            return labels
         
        
        import_components(bitbucket_data['components'])
        # -------------------------------------------------------------
        
        
        
        # attachemnts (ignored - not implemented yet)
        # -------------------------------------------------------------
        # 
        # "attachments":[
        #       // no sample bitbucket_data in our projects
        # ],
        def import_attachments(attachments):
            attachs = []
        
            if options.verbose:
                print 'Importing '+ `len(attachments)` +' attachments(s)...'
        
            print 'ERROR: NOT IMPLEMENTED YET... attachments ignored!'
        
            if options.verbose:
                print 'Done importing attachments.'
        
            return attachs
        
        
        github_data['attachments'] = import_attachments(bitbucket_data['attachments'])
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
        
        def issue_labels(issue):
            labels = []
        
            if options.verbose:
                print 'Extracting all labels from issue: ' + issue['title']
        
            if options.verbose:
                print '- extracting as label : repo name : ' + github_repo
            labels.append(r.get_label(github_repo))
        
            if issue['version'] is not None or type(issue['version']) is str:
                if options.verbose:
                    print '- extracting as label: '+ str(issue['version'])
                labels.append(r.get_label(issue['version']))
        
            if issue['component'] is not None or type(issue['component']) is str:
                if options.verbose:
                    print '- extracting as label: '+ str(issue['component'])
                labels.append(r.get_label(issue['component']))
        
            if issue['priority'] is not None or type(issue['priority']) is str:
                if options.verbose:
                    print '- extracting as label: '+ str(issue['priority'])
                labels.append(r.get_label(issue['priority']))
        
            if issue['kind'] is not None or type(issue['kind']) is str:
                if options.verbose:
                    print '- extracting as label: '+ str(issue['kind'])
                labels.append(r.get_label(issue['kind']))
        
            return labels
        
        def issue_content(issue):
            content = "*original issue: *" # add all missing details after import here
            content += issue['content'].decode('utf-8')
            return content
        
        def import_issues(issues):
            output = {}
            print 'Start importing '+ `len(issues)` +' issues(s)...'
        
            count = 0
            for issue in issues:
                count += 1
                print '- importing #'+ `count`
                if options.verbose:
                    print '- creating new issue "' + issue['title'] + '"'
                if not options.dry_run:
                    title = issue['title']
                    content = issue_content(issue)
                    assignee = issue['assignee']
                    milestone = github_data['milestones'][issue['milestone']]
                    labels = issue_labels(issue)
                    issue = r.create_issue(title, content, assignee, milestone, labels)
                    output['id'] = issue
        
            print 'Done importing issues.'
        
            return output
        
        
        github_data['issues'] = import_issues(bitbucket_data['issues'])
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
        def comment_content(comment):
            # TODO use template to format data
            content = comment['content']
            return content
        
        def import_comments(comments):
            output = []
        
            print 'Start importing '+ `len(comments)` +' comment(s)...'
        
            count = 0
            for comment in comments:
                count += 1
                print '- importing #'+ `count`
                if options.verbose:
                    print '- creating new comment "' + comment['content'] + '"'
                if not options.dry_run:
                    content = comment_content(comment)
                    out = r.create_comment(content)
                    output.append(out)
        
            print 'Done importing comments.'
        
            return output
        
        
        github_data['comments'] = import_comments(bitbucket_data['comments'])
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

        print 'Finished import of '+ bitbucket_repo_name
