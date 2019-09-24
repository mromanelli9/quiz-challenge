# Quiz challenge
A python programming challenge to crate a Quiz-like application.
In order to have an online working prototype,
the application is deployed on Heroku.

### How it works
The game is guided by this few basic rules:
* there is an administrator, a host, who creates and posts questions
(just like a quiz show).
* There are a certain amount of players who, at each new question,
have a button to reserve that question.
* The players can access the game simply join in using their uniques nicknames.
* The admin will have to handle the reservations requests and decide who 'won'
the reservation and allowing only that player to write and send an answer.
* The game cannot continue until an answer is provided for the current question.

For a complete guide, read the [How to play](how_to_play.md) page.

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

## TODO
- [ ] Notification on admin page for when reservations and answers are created.
- [ ] Only one question at a time and that has to be answered before
showing another one.
- [ ] Change how Reservation objects are created (should use forms).

# License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

