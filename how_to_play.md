# Quiz Game - How to play

### The main idea
The game is guided by this few basic rules:
* there is an administrator, a host, who creates and posts questions
(just like a quiz show).
* There are a certain amount of players who, at each new question,
have a button to reserve that question.
* The players can access the game simply join in using their uniques nicknames.
* The admin will have to handle the reservations requests and decide who 'won'
the reservation and allowing only that player to write and send an answer.
* The game cannot continue until an answer is provided for the current question.

# For the players
A player can reach the game by accessing the main page of the web application,
if it is running and available online
(e.g. at `https://this-app.herokuapp.com/`).

### Account creation
The first time you visit the game you'll need to create an account by clicking
on the _Sign_ _Up_ button on the top right of the page.
You need a unique nickname and a password. 
After this step, you'll be automatically redirected to the home page.  
The next time you'll just need to log in using these credentials.

### Home page
The page layout is quite simple: at your left you can see the other players
nickname while at your right is the space for the notifications
(we'll see that later).   
The center of the page is where the questions are displayed.
You can see the content of the question, the text, and a button below which
you need to press in order to reserve the question.
The admin will review the reservations and decide who have won, ideally
based on a first-come-first-served basis.

It could be that there are no question for you to answer. In this case you'll
see written 'No questions available'.
Just wait or try to reload the page.

*NOTE*: While the idea of the game is that quickest to reserve the question
will be allowed to answer as of this moment it's actually at
admin discretion to approve or not a reservation.

### Waiting the reservation approval
When the admin as approved a reservation a notification will appear on the 
right of the page and the 'proceed' button will activate.
If you won the reservation, then you'll be able to provide an answer, otherwise
a message will inform you that you have lost this round.

### Sending the answer
Below the question there is a text area where you have to write the answer
to the question and a button to send it.
Now you have to wait again: the admin as to decide if your answer is correct
or not.  
When he does, a message will notify you and you can proceed to see the result.


# For the admin
The administrator section is accessible from the _admin_ page after the log in
page. If you are running the app locally, this page will probably be located
at `http://127.0.0.1:8000/admin`. 
If the app is available online, let' say at `https://this-app.herokuapp.com`
then the admin page will be at `https://this-app.herokuapp.com/admin`. 

After inserting the credential for the admin user you'll be redirected to the
_Site_ _Administrator_ _page_ where you can see a list of the Django models
used for the applications: _Answers_, _Players_, _Question_ and _Reservation_.
For a basic use of the app, you don't need to worry about all of them, just
_Question_, the abstract representation of a question published in the quiz.  

### _Question_'s model
A _Question_ has several attributes.
* The _question_ _text_ is where you write the question main content.
* The _status_ follows different stages of the question.
    * _Idle_: a fresh, recently-created question will not be visible to the
    players. This allows you to create as many question as you wants
    before the actual start of the game.
    * _Live_: when you want a question to be shown to the players, just set
    this status to a question.
    * _Reserved_: when you have approved a reservation made by one player,
    the question will be reserved and thus not shown anymore to new players.
    * _Closed_: the final stage of a question is reached when the right answer
    is provided (and approved) by the player who as won the reservation.
* The _Reservations_ sections holds a list of all the reservations made by
player to that specific question, order by date, so it'll be easier for you
to decided who one it (if you want to play by the rules).
* _Answers_: holds the answer provided by the player who won the reservation.
It will also have a status: you can decide to approve it, if the answer
is correct, or to reject it, if not.

### First, create a question
The first thing you could do is create the first question.
Click on _Questions_ and then 'Add question' on the top right of the page.
Enter the question you want to create and set the _Status_ on _Live_.
You may leave that if you are creating more than one question and you don't want
them to be available now.  

### Reservations
When a player reserve a question, you'll see a new entry in the _Reservations_
section.
When you are ready, you can approve one of them (ideally the first who made
the reservation) to allow the game to go to the next stage.
Remember that the reservations are ordered by date, so the top one is the first
one made.  

*Note 1*: the first version of the app (v1.0) doesn't have hardcoded restrictions
on approved reservations, so technically you could approve more than one.
However, this is a bit of a nonsense for this game in which the only player 
that is allow to answer is the one who won the reservation.

*Note 2*: As of this moment, there aren't some kind of notifications
for when the players reserve the questions, so to display them you have to
manually refresh the page inside the question change page
(accessible at `Home › Quiz › Questions` and selection the specific question).

### Answers
The player who won the reservation will be asked to provide an answer to the
question that we'll be displayed in the _Answers_ section (don't let the plural
here deceive you, only one answer is allowed).
Now you have to decide if the player provided the correct answer, allowing him
to 'win' the question or not, rejecting his answer.
You do this by selecting the appropriate value for the _Status_ field.
