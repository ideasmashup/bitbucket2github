bitbucket2github
================

basic tools to help migrating from bitbucket to github


## Requirements

First install the python dependencies
```
$ sudo pip install -r requirements.pip
```

You may need to install pip first if you don't have it yet
```
$ sudo apt-get install python-pip
```

Before doing anything **you must prepare all target GitHub repositories** otherwise the import will fail horribly and you'll have to clean up and restart all over again. If you've never done this before just follow the [Migration Guide](help/migration_guide.md)

### Github setup

If you want migrated issues to be assigned properly to actual users you will need to first ask every bitbucket user to create his or her own github account.
After that, you must create at least one target github repository (the migration sript cannot create new repositories), initialized with a readme file.

When it's done complete the config file accordingly, with entries for each user. Unavailable users will be converted to the "importer" user, that's why
it's better practice to import using a "bot" or "neutral" account. Also make sure that all users have access to the target repository and if the repo is
within an organization, make sure to set the org :

```json
	"login" : {
		"github" : {
			"user" : "neutral-user",
			"pass" : "xxx",
			"org"  : "organization-name"
		}
	},
```

### Esxecution

(complete this section) 

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

As described in the [Migration Guide](help/migration_guide.md) if you don't configure a list of users then you won't have any assignees for your issues and the author names won't link to the corresponding GitHub profile.

Images: (example with users in config) (example without)

Configuring this is pretty simple, just use the format below in this example "bituser" becomes "gituser" (while supercoder doesn't change usernames - you should indicate that too):
```
"users" : {
		"bituser" : {
			"bitbucket" : {
				"fullname" : "William WALLACE",
				"mail" : "william@somecompany.com"
			}, 
			"github" : {
				"fullname" : "W. WALLACE",
				"user" : "gituser",
				"mail" : "william@dreamcompany.com"
			}
		},
		"supercoder" : {
			"bitbucket" : {
				"fullname" : "Richie KERNIGAN",
				"mail" : "rkernigan@demigods.cpp"
			}, 
			"github" : {
				"fullname" : "Richie KERNIGAN",
				"user" : "supercoder",
				"mail" : "rkernigan@demigods.cpp"
			}
		},
  }
```

Currently this is only used by the Issues migration script, but in the near future it will also be used to rename all users before importing the git history so that commits also match the github post-migration users infos.
