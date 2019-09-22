# Quiz challenge
A python programming challenge to crate a Quiz-like application.
In order to have an online working prototype,
the application is deployed on Heroku.

## Deployment to Heroku
There are two ways of deploy this app on Heroku.
You can simply connect your GitHub account and specify in which repository
your application is, or you can use the Heroku CLI.
```
$ heroku login

$ git init
$ git add -A
$ git commit -m "Initial commit"

$ heroku create
$ git push heroku master

$ heroku run python manage.py migrate
```

## Folder structure
Instead of using the common Django folder structure, here I've used a template
that makes easier the deployment on Heroku.
You can find the template [here](https://github.com/heroku/heroku-django-template).

# License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

