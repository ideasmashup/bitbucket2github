#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import pystache
import os
import traceback

# parse parameters and show help
from optparse import OptionParser
from github.GithubException import GithubException
from types import NoneType

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

parser.add_option("-f", "--file", dest="json_file", default=None,
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
COLOR_SUBTREE   = "66cc00"
COLOR_KIND      = "cccc00"
COLOR_PRIORITY  = "ff6600"

count = 0
github_data = {}
bitbucket_data = {}

github_login = None
github_password = None
github_org = None
bitbucket_repo = None
github_merge_repo = None
github_repo = None
github_subtree = None


def si(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj


def so(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
        else:
            obj = obj.decode(encoding) 
    return obj

# colors and text styles

HEADER = '\033[95m'
STRONG = '\033[94m'
EM = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = "\033[1m"

if options.verbose:
    print BOLD + HEADER + 'BitBucket to GitHub v0.7' + ENDC


def get_script_path():
    return os.path.dirname(os.path.realpath(__file__))


def load_json(filename):
    data = None
    
    if type(filename) is not NoneType:
        if options.verbose:
            print 'Loading data from JSON file: ' + HEADER + filename + ENDC
    
        try:
            ujson = si(open(filename).read())
            data = json.loads(ujson)
            if options.verbose:
                print '- loaded ' + `len(ujson)` + ' bytes'
                # pprint(data)
        except Exception:
            print FAIL + traceback.format_exc() + ENDC
            exit(-1)

    return data


# load config file
if options.config_file is not None:
    config = load_json(options.config_file)

# connect to GitHub API v3 
# see: https://github.com/jacquev6/PyGithub
# see: https://developer.github.com/v3/
from github import Github

if not options.dry_run:
    if config is not None and config['login']['github']['user'] is not None:
        github_login = si(config['login']['github']['user'])
        if options.verbose:
            print '- fetching login from config file ' + HEADER + github_login + ENDC
    elif options.github_login is not None:
        github_login = si(options.github_login)
        if options.verbose:
            print '- fetching login from script -u parameter value ' + HEADER + github_login + ENDC
    else:
        github_login = si(raw_input('Please enter your github login: '))

    if config is not None and config['login']['github']['pass'] is not None:
        github_password = si(config['login']['github']['pass'])
        if options.verbose:
            print '- fetching password from config file ' + HEADER + ('*' * len(github_password))[:len(github_password)] + ENDC
    else:
        print STRONG + 'Please enter your github password: ' + ENDC
        github_password = si(getpass.getpass())

    if options.verbose:
        print '- connecting to GitHub using: ' + HEADER + github_login + ' ' + ('*' * len(github_password))[:len(github_password)] + ENDC

    g = Github(github_login, github_password)

    # fetch then loop through all repos entries from the config file
    if config is not None and config.get('repos') is not None:
        bitbucket_repos = si(config['repos'])
    else:
        bitbucket_repos = {}

    # global merge repo
    if config is not None and config.get('merge_repo') is not None:
        github_merge_repo = si(config['merge_repo'])
        if options.verbose:
            print '- fetching merge repo from config file ' + HEADER + github_merge_repo + ENDC


    for bitbucket_repo_name, bitbucket_repo in bitbucket_repos.iteritems():
        if options.verbose:
            print 'Start importing repo ' + HEADER + bitbucket_repo_name + ENDC

        if bitbucket_repo['merge'] is False:
            github_repo = si(bitbucket_repo['name'])
            github_subtree = None
        elif bitbucket_repo['merge'] is True and github_merge_repo is not None:
            github_repo = si(github_merge_repo)
            github_subtree = si(bitbucket_repo['name'])
        else:
            github_repo = si(bitbucket_repo['merge'])
            github_subtree = si(bitbucket_repo['name'])

        if options.verbose:
            if github_subtree is not None:
                print '- imported as ' + HEADER + BOLD + github_repo + ENDC + ' ' +  HEADER + github_subtree + ENDC
            else:
                print '- imported as ' + HEADER + BOLD + github_repo + ENDC

        # check if must use org or not
        if config is not None and 'org' in config['login']['github']:
            github_org = si(config['login']['github']['org'])
            if options.verbose:
                print '- will use organization as repository parent: '+ HEADER + github_org + ENDC
            # load organization repo
            try:
                r = g.get_organization(github_org).get_repo(github_repo)
                print 'Opening GitHub '+ github_org +' repository: ' + HEADER + r.name + ENDC
            except GithubException:
                print 'Github repository '+ github_repo +' can\'t be accessed by '+ github_login +' check permissions and/or initialize the repository with a file, then try again.'
                print FAIL + traceback.format_exc() + ENDC
                exit(-1)
        else:
            # load user repo
            try:
                r = g.get_user().get_repo(github_repo)
                print 'Opening  '+ github_login +' GitHub repository: ' + HEADER + r.name + ENDC
            except GithubException:
                print 'Github repository '+ github_repo +' does not exist yet! create it !'
                print FAIL + traceback.format_exc() + ENDC
                exit(-1)

        # load issues json file
        # -------------------------------------------------------------
        if config is not None and 'issues' in bitbucket_repo and type(bitbucket_repo['issues']) is not NoneType:
            if type(bitbucket_repo['issues']) is bool:
                # FIXME implement online import by connecting to bitbucket's REST API to solve this 
                print WARNING + 'You must indicate a JSON file from where to import the issues data. Genereate this file from the Bitbucket repo settings page.' + ENDC
                print FAIL + 'Skipping import of this Repository issues.' + ENDC
                continue
            else:
                # load issues from JSON file specified in repository config file etry
                bitbucket_data = load_json(bitbucket_repo['issues'])
        else:
            bitbucket_data = load_json(options.json_file)
        # -------------------------------------------------------------
        
        # make github imported data dict
        if github_data is None:
            github_data = {
                # inject empty dict sections later
            }
            
        
        if github_repo not in github_data:
            github_data[github_repo] = {
                    'metas' : {},
                    'milestones' : {},
                    'kinds' : {},
                    'priorities' : {},
                    'versions' : {},
                    'components' : {},
                    'attachments' : {},
                    'issues' : {},
                    'users' : {},
                    'comments' : {},
                }
        
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
            if options.verbose:
                print 'Importing '+ `len(metas)` +' default value(s)...'
        
            count = 0
            for key, value in metas.items():
                if key is not None and si(key) in github_data[github_repo]['metas']:
                    # check if already imported
                    print '- already imported: '+ si(value)
                    continue
                
                elif key is not None and value is not None:
                    # import for the first time
                    count += 1
                    print '- importing default #'+ `count` 
                    if options.verbose:
                        print '- default '+ si(key) +' = '+ si(value) 
                    if not options.dry_run:
                        github_data[github_repo]['metas'][si(key)] = si(value)
        
            print 'Done importing default values.'
        
        # defaults from meta fields
        import_metas(bitbucket_data['meta'])
        
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
            if options.verbose:
                print 'Importing '+ `len(milestones)` +' milestone(s)...'
        
            count = 0;
            for milestone in milestones:
                if si(milestone['name']) in  github_data[github_repo]['milestones']:
                    print '- milestone already exists: '+ si(milestone['name']) +' keeping existing one'
                    continue
            
                count += 1
                print '- importing #'+ `count`
                if options.verbose:
                    print '- creating new "' + si(milestone['name']) + '" milestone with no description and deadline set to ('+ si(DEFAULTS['date'].strftime("%Y-%m-%dT%H:%M:%SZ")) +')'
                if not options.dry_run:
                    try:
                        out = r.create_milestone(milestone['name'], "open", "", datetime.date.today())
                        github_data[github_repo]['milestones'][si(milestone['name'])] = out
                    except GithubException:
                        # FIXME find a way to fetch the existing milestones
                        # m = r.get_milestone(number)
                        # github_milestones[milestone['name']]
                        print FAIL + '- failed to create milestone: ' + ENDC
                        print FAIL + traceback.format_exc() + ENDC
            print 'Done importing milestones.'


        import_milestones(bitbucket_data['milestones'])
        
        if options.verbose:
            print 'Imported milestones :'
            for mobj in github_data[github_repo]['milestones']:
                print '- '+ mobj.title()
        # -------------------------------------------------------------
        
        
        
        # -------------------------------------------------------------
        github_data[github_repo]['labels'] = {}
        
        def add_label(label):
            github_data[github_repo]['labels'][si(label.name)] = si(label)
        
        
        def get_label(name):
            label = None
            name = si(name)
            if name in github_data[github_repo]['labels']:
                label = github_data[github_repo]['labels'][name]
            else:
                try:
                    label = r.get_label(name)
                except:
                    print FAIL + '- failed to find label: '+ name + ENDC
                
            return label
        
        def create_label(name, color):
            label = None
            name = si(name)
            
            if name in github_data[github_repo]['labels']:
                print '- label '+ HEADER + si(name) + ENDC + ' already exists, keeping previous one'
                return github_data[github_repo]['labels'][si(name)]
                
            if options.verbose:
                print '- creating new label "' + HEADER + name + ENDC + '"'
            if not options.dry_run:
                try:
                    label = r.create_label(name, color)
                    add_label(label)
                except GithubException:
                    label = r.get_label(name)
                    if label is not None:
                        print WARNING + '- label already exists, fetching existing value: '+ name + ENDC
                        label = r.get_label(name)
                        add_label(label) 
                    else:
                        print FAIL + '- failed to create label: ' + name + ENDC
                        print FAIL + traceback.format_exc() + ENDC

            return label
        # -------------------------------------------------------------
        
        # create label for repository (for multi-repos merges?)
        create_label(github_repo, COLOR_REPOS)
        if github_subtree is not None:
            create_label(github_subtree, COLOR_REPOS)
        
        # import issues kinds and priorities as labels
        # -------------------------------------------------------------
        def import_kinds():
            # only import as labels when they don't exist already
            labels = ['proposal', 'task']
        
            if options.verbose:
                print 'Importing '+ `len(labels)` +' (s)...'
        
            count = 0
            for name in labels:
                count += 1
                print '- importing #'+ `count`
                if not options.dry_run:
                    create_label(name, COLOR_KIND)
            
            if options.verbose:
                print 'Done importing kinds.'
            
        
        def import_priorities():
            labels = ['major', 'trivial', 'minor', 'critical', 'blocker']
        
            if options.verbose:
                print 'Importing '+ `len(labels)` +' (s)...'
        
            count = 0
            for name in labels:
                count += 1
                print '- importing #'+ `count`
                if not options.dry_run:
                    create_label(name, COLOR_PRIORITY)
                
            if options.verbose:
                print 'Done importing priorities.'
                
        
        
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
            if options.verbose:
                print 'Importing '+ `len(versions)` +' version(s)...'
        
            count = 0
            for version in versions:
                count += 1
                print '- importing #'+ `count`
                if not options.dry_run:
                    create_label(version['name'], COLOR_VERSION)
            
            if options.verbose:
                print 'Done importing versions.'
        
        
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
            if options.verbose:
                print 'Importing '+ `len(components)` +' component(s)...'
        
            count = 0
            for component in components:
                count += 1
                print '- importing #'+ `count`
                if not options.dry_run:
                    create_label(component['name'], COLOR_VERSION)
        
            if options.verbose:
                print 'Done importing components.'
         
        
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
        
#             if 'attachments' in github_data[github_repo] and name in  github_data[github_repo]['attachments']:
#                 print '- attachment '+ si(name) + ' already exists, keeping previous one'
#                 return github_data[github_repo]['attachments'][si(name))]
            
            print 'ERROR: NOT IMPLEMENTED YET... attachments ignored!'
        
            if options.verbose:
                print 'Done importing attachments.'
        
            return attachs
        
        
        github_data[github_repo]['attachments'] = import_attachments(bitbucket_data['attachments'])
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
        
        def load_template(filename):
            ext = '.md'
            tpl_path = get_script_path() +'/templates/'+ filename + ext
            
            if os.path.isfile(filename):
                None # do nothing because filepath is ok
            elif os.path.isfile(tpl_path):
                filename = tpl_path # default template dir 
            elif os.path.isfile(filename + ext):
                filename = filename + ext # template without extension

            if options.verbose:
                print 'Loading template file: ' + HEADER + filename + ENDC
            
            try:
                return si(open(filename).read())
            except Exception:
                print FAIL + traceback.format_exc() + ENDC
                exit(-1)
        
        def prepare_issue(issue):
            # inject new keys into issue for proper rendering of templae
            if config is not None and 'users' in config and issue['reporter'] in config.get('users'):
                try:
                    issue['github_reporter'] = si(config['users'][issue['reporter']]['github']['user'])
                    issue['github_reporter_full'] = si(config['users'][issue['reporter']]['github']['fullname'])
                except Exception:
                    print FAIL + traceback.format_exc() + ENDC
            else: 
                # if cannot find convertible user, use current user
                issue['github_reporter'] = github_login 
                issue['github_reporter_full'] = '( '+ si(issue['reporter']) +' )'
            return issue
        
        def convert_user(bitbucket_username):
            # by default the "importer" user name is used
            github_username = github_login

            # otherwise use config file 'users' entries
            if config is not None and 'users' in config and bitbucket_username in config.get('users'):
                try:
                    github_username = si(config['users'][bitbucket_username]['github']['user'])
                except Exception:
                    print FAIL + traceback.format_exc() + ENDC
                if options.verbose:
                    print 'converted '+ bitbucket_username +' as '+ github_username 
            return github_username
        
        def issue_labels(issue):
            labels = []
        
            if options.verbose:
                print 'Extracting all labels from issue: ' + issue['title']
        
            if options.verbose:
                print '- extracting as label : repo name : ' + github_repo
            labels.append(get_label(github_repo))
        
            if issue['version'] is not None:
                if options.verbose:
                    print '- extracting as label: '+ issue['version'].encode('utf-8')
                labels.append(get_label(issue['version']))
        
            if issue['component'] is not None:
                if options.verbose:
                    print '- extracting as label: '+ issue['component'].encode('utf-8')
                labels.append(get_label(issue['component']))
        
            if issue['priority'] is not None:
                if options.verbose:
                    print '- extracting as label: '+ issue['priority'].encode('utf-8')
                labels.append(get_label(issue['priority']))
        
            if issue['kind'] is not None:
                if options.verbose:
                    print '- extracting as label: '+ issue['kind'].encode('utf-8')
                labels.append(get_label(issue['kind']))
            
            if bitbucket_repo['merge'] is False:
                labels.append(get_label(si(github_repo)))
            elif bitbucket_repo['merge'] is True and github_merge_repo is not None:
                labels.append(get_label(si(github_merge_repo)))
                labels.append(get_label(si(bitbucket_repo['name'])))
            else:
                labels.append(get_label(si(bitbucket_repo['merge'])))
                labels.append(get_label(si(bitbucket_repo['name'])))
    
            if options.verbose:
                if github_subtree is not None:
                    print '- added repo labels ' + github_repo + ' and ' + github_subtree
                else:
                    print '- added repo label ' + github_repo
        
            return labels
        
        def issue_content(issue):
            content = pystache.render(load_template('issue'), prepare_issue(issue))
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
                    if 'title' in issue and issue['title'] is not None:
                        title = si(issue['title'])
                    else:
                        title = 'Untitled #'+ si(issue['id'])
                    
                    if 'content' in issue and issue['content'] is not None:
                        content = si(issue_content(issue))
                    else:
                        content = ''
                    
                    if 'assignee' in issue and issue['assignee'] is not None:
                        assignee = si(convert_user(issue['assignee']))
                    else:
                        assignee = None # no assignee
                    
                    if 'milestone' in issue and issue['milestone'] is not None:
                        milestone = si(github_data[github_repo]['milestones'][si(issue['milestone'])])
                    else:
                        milestone = None # assign no milestone 
                    
                    labels = issue_labels(issue)
                    
                    try:
                        # FIXME cannot use NotSet
                        if assignee is None:
                            out = r.create_issue(title, content)
                        elif milestone is None:
                            out = r.create_issue(title, content, assignee)
                        else:
                            out = r.create_issue(title, content, assignee, milestone, labels)
                        
                        output[issue['id']] = out
                    except GithubException:
                        print FAIL + '- failed to create issue #' + str(issue['id']) + ENDC
                        print FAIL + traceback.format_exc() + ENDC
        
            print 'Done importing issues.'
        
            return output
        
        
        github_data[github_repo]['issues'] = import_issues(bitbucket_data['issues'])
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
        
        def prepare_comment(comment):
            # inject new keys into issue for proper rendering of templae
            if config is not None and 'users' in config and comment['user'] in config.get('users'):
                try:
                    comment['github_user'] = si(config['users'][comment['user']]['github']['user'])
                    comment['github_user_full'] = si(config['users'][comment['user']]['github']['fullname'])
                except Exception:
                    print FAIL + traceback.format_exc() + ENDC
            else: 
                # if cannot find convertible user, use current user
                comment['github_reporter'] = github_login 
                comment['github_reporter_full'] = '( '+ si(comment['user']) +' )'
            return comment
        
        def comment_content(comment):
            content = pystache.render(load_template('comment'), prepare_comment(comment))
            return content
        
        def import_comments(comments):
            output = []
        
            print 'Start importing '+ `len(comments)` +' comment(s)...'
        
            count = 0
            for comment in comments:
                # skip all null content comments (usually just minor fields updates so not useful)
                if comment['content'] is None or type(comment['content']) is NoneType:
                    print '- skipping comment because it is either null or None...'
                    continue
                else:
                    count += 1
                    print '- importing #'+ str(comment['id'])
                    if options.verbose:
                        print '- creating new comment "' + si(comment['content']) + '"'
                    if not options.dry_run:
                        content = comment_content(comment)
                        if comment['issue'] in github_data[github_repo]['issues']:
                            issue = github_data[github_repo]['issues'][comment['issue']]
                            if options.verbose:
                                print '- creating new comment for issue #'+ str(comment['issue'])
                            try:
                                out = issue.create_comment(si(content))
                                output.append(out)
                            except GithubException:
                                print FAIL + '- failed to create issue comment #' + str(comment['id']) + ENDC
                                print FAIL + traceback.format_exc() + ENDC
                        else:
                            if options.verbose:
                                print '- failed to import comment because issue #'+ str(comment['issue']) + ' not found!' 
        
            print 'Done importing comments.'
        
            return output
        
        
        github_data[github_repo]['comments'] = import_comments(bitbucket_data['comments'])
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
        
        # FIXME maybe import as "changelog" .md files in source or wiki?
        print '- logs import not implemented' 
#         for log in logs:
#             if options.verbose:
#                 print '- creating new log "' + log['content'] + '"'
        #     if not options.dry_run:
        #         r.create_issue(title, comment['content'], assignee, milestone, labels)
        
        print 'Done importing logs.'
        # -------------------------------------------------------------

        print 'Finished import of '+ bitbucket_repo_name
