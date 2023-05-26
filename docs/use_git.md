# Git Handbook

## Something to check before you start any of the steps below
### 1. temp file discarding
- Make sure your repository do not contain auto generated files by other softwares like *.vscode* folder. If you have any folders or files like that, you need to add the full name to [**.gitignore**](.gitignore) file. For example:
```
# Discard vscode file
.vscode
```
### 2. Conflict handling
- Make sure you know how to deal with code conflict. Since we all editing the same file **main.ipynb**, git will give us a conflict warning and stop our operation.
- use **stash** or **merge** to solve any issue

## clone the repository
- This is used when you don't have the repository in your local machine
```console
$ git clone git@github.com:hungry5656/NetflixRecommendation.git
```
## add your code
```console
$ git add <file> # add some specific file that you changed
$ git add -A # add all changes
```

## commit your code
- In the message, it is better to use format **"\<action> \<what you did> in \<section name>"**
- example: *"add model fitting in training section"*
```console
$ git commit -m "the message for this commit"
```

## push your code to github
```console
$ git push
```

## pull updated code from github
```console
$ git pull
```
## stash

## merge