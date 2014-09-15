#!/usr/bin/env python
import os

"""

"""

"""
	Config variables
"""

# bitbucket login
bb_user = "user"
bb_pass = "pass"

# github login
gh_user = "me"
gh_pass = "password"

# project-name where to move the 
projects_merge_root = "my_project"
projects_merge_path = "./"

# list of projects and merging options
projects = [
    {
        "bb_name" : "project1",
        "gh_name" : "company",
        "merge"   : False,
    },
    {
        "bb_name" : "project2",
        "gh_name" : "project2",
        "merge"   : True,
    },
    {
        "bb_name" : "project3",
        "gh_name" : "project3",
        "merge"   : True,
    }
]


"""
    # USERS/COMMITERS TO CONVERT IN GIT REPOSITORIES
    {
        "bb" : {
            "name" : "",
            "mail" : "",
        },
        "gh" : {
            "name" : "",
            "mail" : "",
        },
    },
"""
users = [
    {
        "bb" : {
            "name" : "",
            "mail" : "",
        },
        "gh" : {
            "name" : "",
            "mail" : "",
        },
    },
    {
        "bb" : {
            "name" : "",
            "mail" : "",
        },
        "gh" : {
            "name" : "",
            "mail" : "",
        },
    },
    {
        "bb" : {
            "name" : "",
            "mail" : "",
        },
        "gh" : {
            "name" : "",
            "mail" : "",
        },
    },
    {
        "bb" : {
            "name" : "",
            "mail" : "",
        },
        "gh" : {
            "name" : "",
            "mail" : "",
        },
    },
    {
        "bb" : {
            "name" : "",
            "mail" : "",
        },
        "gh" : {
            "name" : "",
            "mail" : "",
        },
    }
}


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

