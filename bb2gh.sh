#!/bin/sh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

mkdir ~/bb2gh_temp
cd ~/bb2gh_temp
mkdir .bitbucket
cd .bitbucket/
git clone git clone git@bitbucket.org:smartificiel/blep-android.git/wiki
git clone git@bitbucket.org:smartificiel/blep-android.git/wiki
ls -al
mv wiki android.wiki
ls -al
git clone git@bitbucket.org:smartificiel/blep-arduino.git/wiki
mv wiki arduino.wiki
ls -al
git clone git@bitbucket.org:smartificiel/blep-general.git/wiki
ls -al
mv wiki general.wiki
ls -al
ls -al general.wiki/
cd ~/bb2gh_temp
mkdir .github
cd .github/
ls -al
cd test/
ls -al
touch README.md
ls -al
git init
git add README.md 
git commit -am "Initial commit"
git status
git remote add -f android ~/bb2gh_temp/.android/blep-android
git merge android/master 

ls -al

cd ..
rm -rf test
mkdir test
cd test/
git init
touch README.md
git add README.md 
git commit -m "Initial commit"

mkdir android
mkdir arduino
mkdir general
ls -al
cd android/
git remote add -f android ~/bb2gh_temp/.android/blep-android
ls -al
cd ..
ls -al
git merge android/master 
ls -al
mv Speech_Recognition android/
mv VoiceRecognitio android/
mv VoiceRecognition android/
ls -al

git reset --hard
ls -al
git rm README.md 
git commit -m "deleted dummy readme file"
dir -exclude android | %{git mv $_.Name android}
rm -rf *
ls -al
cd ..
rm -rf test/
ls -al
mkdir test
cd test/
git init
cd ..
rm -rf test/
git clone git@github.com:ideasmashup/test.git
cd test/
ls -al
git remote add -f projectb /path/to/other/repo
git remote add -f android ~/bb2gh_temp/.android/blep-android
ls -al
git merge -s ours --no-commit android/master
git read-tree --prefix=android/ -u android/master
ls -al
git commit -m "Merge bitbucket blep-android into android/"

ls -al
git remote add -f  /path/to/other/repo
git merge -s ours --no-commit arduino/master
git read-tree --prefix=arduino/ -u arduino/master

git status
git reset --hard

git status
git merge -s ours --no-commit arduino/master
git read-tree --prefix=arduino/ -u arduino/master
git status


cd arduino/
ls -al
cd ..
ls -al
cd ..
ls -al
git clone git@github.com:ideasmashup/test.wiki.git
ls -al
cd test.wiki/
ls -al
git remote add -f general ~/bb2gh_temp/.bitbucket/general.wiki
git merge -s ours --no-commit general/master
git read-tree --prefix=general/ -u general/master
git commit -m "Merge bitbucket blep-general wiki into general/"
ls -al
git remote add -f android ~/bb2gh_temp/.bitbucket/android.wiki
git merge -s ours --no-commit android/master
git read-tree --prefix=android/ -u android/master
git commit -m "Merge bitbucket blep-android wiki into android/"
ls -al
git remote add -f arduino ~/bb2gh_temp/.bitbucket/arduino.wiki
git merge -s ours --no-commit arduino/master
git read-tree --prefix=arduino/ -u arduino/master
git commit -m "Merge bitbucket blep-arduino wiki into arduino/"
ls -al
cd ..
ls -al
cd test.wiki/
git push origin master 
ls -al
cd android/
ls -al
cd ..
git pull

git reset --hard
ls -al


sh $DIR/git-author-rewrite.sh ./

git push --force --tags origin 'refs/heads/*'
