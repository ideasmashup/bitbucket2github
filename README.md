bitbucket2github
================

basic tools to help migrating from bitbucket to github


## Requirements

First install the python dependeancies
```
$ sudo pip install -r requirements.pip
```

You may need to install pip first if you don't have it yet
```
$ sudo apt-get install python-pip
```

## Tools

### Source

(complete this section)

### Issues

```import_issues.py``` can import all issues from a bitbucket issues export file
into the github project of your choice. Currently only supports the uncompressed
json file (usually the ```db-1.0.json``` file within ```{project}_issues.zip```)

```
$ import_issues.py -h
Usage: import_issues.py [options]

Options:
  -h, --help            show this help message and exit
  -t, --dry-run         Perform a dry run and print eveything.
  -u GITHUB_LOGIN, --username=GITHUB_LOGIN
                        Username of target GitHub account.
  -r REPOSITORY, --repository=REPOSITORY
                        GitHub repository where to import the issues
  -f JSON_FILE, --file=JSON_FILE
                        Source JSON file containing the issues to import

$ import_issues.py -u username -r repository -f db-1.0.json
```

### Wiki

(complete this section)

### Downloads

(not supported yet...) 

### Users

(complete this section)