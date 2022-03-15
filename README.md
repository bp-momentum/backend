# BP-backend

## Setup

### Database
To create a PostgreSQL database, please refer to this very useful [guide](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart-de).

### Entrypoint
Inside the `BPBackendDjango` directory, you will find a file called `manage.py`. This is the main entrypoint for all operations with
this Django backend server.

### Configuration
To create a default configuration, please start the server once, by running `python3 manage.py runserver <host-address>:<port>`.
After that you will find a newly created `settings.json` file inside the directory. Now you can open the file and enter you configuration.
You don't have to fill in the `token_key` object inside the json, as it will be created automatically upon the first server start.

First you have to give the information for the email-service. Here you need to give your email address, your password and the 
smtp server (for gmail: smtp.gmail.com). Then you can change the standard admin trainer and user
details. These users will created only once when you firstly start the server. 

Now you have to give the database information which you defined while creating 
the database. "name" is here the database name, which you want to use and must be already created.

"video_dir" is the relative path to the video folder, where the videos are stored.

The secret key doesn't have to be changed. This is a random 16 long string.


The allowed origins are the urls from where the server can be reached.
Here you should give the frontend url and maybe the localhost addresses for testing.
For the website url you have to give the url of the frontend.

last_leaderboard_reset should not be changed.

### Starting the Server
Before starting the server the database must create the tables.
For this type the command "python manage.py makemigrations" and
"python manage.py migrate". Now the database will be adjusted, and the tables will be created.

After configuration, please start the server by running `python3 manage.py runserver <host-address>:<port>` again.
If there are any issues with your settings, you will see errors in the output. After successfully starting the server, it will
be reachable at your `<host-address>:<port>`. The admin panel will be reachable at `<host-address>:<port>/admin`.
As an example you can type the command "python manage.py runserver 0.0.0.0:8000"

Now the server can be reached by the frontend if the ports are allowed in the firewall.


## Api Documentation
### Create User and Trainer

Method: POST 

Path: /api/createuser

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "first_name": <str>,
    "last_name": <str>,
    "username": <str>,
    "email_address": <str>,
    "url": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "User was successfully created",
    "data": {}
}
```

### Login

Method: POST 

Path: /api/login

Parameters: 
```json
{
    "username": <str>,
    "password": <str>,
}
```
Success Return 

```json
{
    "success": true,
    "description": "User is now logged in",
    "data": {
        "session_token": session_token,
        "refresh_token": refresh_token
    }
}
```

### Register

Method: POST 

Path: /api/register

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "new_user_token": <str>,
    "password": <str>,
    "username": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "User was created",
    "data": {
        "session_token": <str>,
        "refresh_token": <str>
    }
}
```

### Logout all devices

Method: POST 

Path: /api/logoutdevices

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{}
```
Success Return 

```json
{
    "success": true,
    "description": "refresh-token changed",
    "data": {
        "refresh-token": <str>,
        "session_token": <str>
    }
}
```

### Login via refresh-token

Method: POST 

Path: /api/auth

Header:
```json
{
}
```

Parameters: 
```json
{
    "refresh_token": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "user is now logged in",
    "data": {
        "session_token": <str>,
        "refresh-token": <str>
        }
}
```

### Delete Account

Method: POST 

Path: /api/deleteaccount

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{}
```

Success Return 

```json
{
    "success": true,
    "description": "User was successfully deleted",
    "data": {}
}
```

### Change Language

Method: POST 

Path: /api/changelanguage

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "language": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "language was successfully changed",
    "data": {}
}
```

### Get Language

Method: GET 

Path: /api/getlanguage

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
}
```
Success Return 

```json
{
    "success": true,
    "description": "language returned",
    "data": {
        "language": <str>
    }
}
```

### Get Users of Trainer

Method: GET (as trainer) or POST as admin 

Path: /api/gettrainersuser

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "username": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Returned users of trainer",
    "data": {
        "users": <list>[{
            "id": <int>,
            "username": <str>,
            "plan": <int>,
            "done_exercises": <float>,
            "last_login": <str>
        }]
    }
}
```

### Get Trainers

Method: GET

Path: /api/gettrainers

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
}
```
Success Return 

```json
{
    "success": true,
    "description": "Returning all trainers",
    "data": {
        "trainers": <list>[{
            "id": <int>,
            "username": <str>,
            "last_login": <str>
        }]
    }
}
```

### Delete Trainer

Method: POST

Path: /api/deletetrainer

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "id": <int>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Trainer was deleted",
    "data": {}
}
```

### Delete User

Method: POST

Path: /api/deleteuser

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "id": <int>
}
```
Success Return 

```json
{
    "success": true,
    "description": "User was deleted",
    "data": {}
}
```

### Get User Level

Method: GET

Path: /api/getuserlevel

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "username": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "returning level and progress of next level",
    "data": {
        "level": <int>,
        "progress": <str>
    }
}
```

### Get Invited User

Method: GET

Path: /api/getinvited

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
}
```
Success Return 

```json
{
    "success": true,
    "description": "Returning created invites",
    "data": {
        "invited": <list>[{
            "id": <int>,
            "first_name": <str>,
            "last_name": <str>,
            "email": <str>
        }]
    }
}
```

### Invalidate Invite

Method: POST

Path: /api/invalidateinvite

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "id": <int>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Token invalidated",
    "data": {}
}
```

### Change Username

Method: POST

Path: /api/changeusername

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "username": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Username changed",
    "data": {
        "session_token": <str>,
        "refresh_token": <str>
    }
}
```

### Change Password

Method: POST

Path: /api/changepassword

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "password": <str>,
    "new_password": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Password changed",
    "data": {
        "session_token": <str>,
        "refresh_token": <str>
    }
}
```

### Change Avatar

Method: POST

Path: /api/changeavatar

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "avatar": <int>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Avatar changed",
    "data": {}
}
```

### Change Motivation

Method: POST

Path: /api/changemotivation

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "motivation": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Motivation changed",
    "data": {}
}
```

### Get Profil

Method: GET

Path: /api/getprofile

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{}
```
Success Return 

```json
{
    "success": true,
    "description": "Returning profile data",
    "data": {
        "username": <str>,
        "avatar": <int>,
        "first_login": <str>,
        "motivation": <str>
    }
}
```

### Get Trainer Contact

Method: GET

Path: /api/gettrainercontact

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{}
```
Success Return 

```json
as user:
{
    "success": true,
    "description": "Returning contact data of trainer",
    "data": {
        "name": <str>,
        "address": <str>,
        "telephone": <str>,
        "email": <str>
    }
}
as trainer:
{
    "success": true,
    "description": "Returning your contact data",
    "data": {
        "name": <str>,
        "academia": <str>,
        "street": <str>,
        "city": <str>,
        "country": <str>,
        "address_addition": <str>,
        "postal_code": <str>,
        "house_nr": <str>,
        "telephone": <str>,
        "email": <str>
    }
}
```

### Set Trainer Location

Method: POST

Path: /api/changelocation

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "street": <str>,
    "city": <str>,
    "country": <str>,
    "address_addition": <str>,
    "postal_code": <str>,
    "house_nr": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Location updated",
    "data": {}
}
```

### Set Trainer Telephone Number

Method: POST

Path: /api/changetelephone

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "telephone": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Telephone number updated",
    "data": {}
}
```

### Set Trainer Academia

Method: POST

Path: /api/changeacademia

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "academia": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Academia updated",
    "data": {}
}
```

### Search User

Method: POST

Path: /api/searchuser

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "search": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "returning list of matching users",
    "data": {
        "users": <list>[{
            "id": <int>,
            "username": <str>
        }]
    }
}
```

### Get List of Users

Method: GET

Path: /api/getlistofusers

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{}
```
Success Return 

```json
{
    "success": true,
    "description": "returning list of users",
    "data": {
        "users": <list>[{
            "id": <int>,
            "username": <str>
        }]
    }
}
```

### Get Reset Password Mail

Method: POST

Path: /api/getresetpasswordemail

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "username": <str>,
    "url": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "email with invite was sent",
    "data": {}
}
```

### Reset Password

Method: POST

Path: /api/resetpassword

Header:
```json
{
}
```

Parameters: 
```json
{
    "reset_token": <str>,
    "new_password": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Password got reset",
    "data": {}
}
```

### Get exercise

Method: GET 

Path: /api/getexercise

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "id": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Returned data",
    "data": {
        "title": <str>,
        "description": <str>,
        "video": <str>
    }
}
```

### Get exercise list

Method: GET 

Path: /api/getexerciselist

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
}
```
Success Return 

```json
{
    "success": true,
    "description": "list of exercises is provided",
    "data": {
        "exercise_list": <list>[{
                "id": <int>,
                "title": <str>
                }]
    }
}
```


### Get Done Exercise

Method: GET when user else POST

Path: /api/getdoneexercises

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "user": <str> #only when trainer
}
```
Success Return 

```json
{
    "success": true,
    "description": "Returned list of Exercises and if its done",
    "data": {
            "name": <str>,
            "done": <list>[{
                          "exercise_plan_id": <int>,
                          "id": <int>,
                          "sets": <int>,
                          "repeats_per_set": <int>,
                          "date": <str>,
                          "done": <bool>
                        }]
        }
}
```

### Get Done Exercises for month

Method: POST

Path: /api/getdoneexercisesinmonth

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "month": <int>,
    "year": <int>
}
```
Success Return 

```json
{
    "success": true,
    "description": "returned plan",
    "data": {
            "done": <list>[{
                            "exercise_plan_id": <int>,
                            "id": <int>,
                            "date": <int>,
                            "points": <int>,
                            "done": <bool>
                        }]
        }
}
```

### Create plan

Method: POST 

Path: /api/createplan

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "name": <str>,
    "exercise": <list of dict> ({
        "date": <str>,
        "sets": <str>,
        "repeats_per_set": <str>,
        "id": <str>
        }),
    "id": <int> //only if plan should be changed
}
```
Success Return 

```json
{
    "success": true,
    "description": "plan created",
    "data": {
        "plan_id": plan.id
    }
}
```

### assign plan to user

Method: POST 

Path: /api/addplantouser

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "user": <str>,
    "plan": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "plan assigned to user",
    "data": {}
}
```

### Get List of Plans
Method: GET 

Path: /api/getlisofplans

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{}
```
Success Return 

```json
{
    "success": true,
    "description": "returning all plans",
    "data": {
        "plans": <list>[{
            "id": <int>,
            "name": <str>
        }]
    }
}
```

### Get Plan

Method: POST 

Path: /api/getplan

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "plan": <int>
}
```
Success Return 

```json
{
    "success": true,
    "description": "returned plan",
    "data": {
            "name": <str>,
            "exercises": <list>[{
                          "exercise_plan_id": <int>,
                          "id": <int>,
                          "sets": <int>,
                          "repeats_per_set": <int>,
                          "date": <str>
                        }]
        }
}
```

### Get Plan of User

Method: POST 

Path: /api/requestplanofuser

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters:
for users: 
```json
{}
```
for trainers:
```json
{
    "username": <str> //only needed if called as trainer
}
```
Success Return 

as user:
```json
{
    "success": true,
    "description": "returned plan of this account",
    "data": {
            "exercises": <list>[{
                "exercise_plan_id": <int>,
                "id": <int>,
                "sets": <int>,
                "repeats_per_set": <int>,
                "date": <str>
            }]
        }
}
```
as trainer:
```json
{
    "success": true,
    "description": "returned plan of user",
    "data": {
            "exercises": <list>
        }
}
```

### Delete Plan

Method: POST 

Path: /api/deleteplan

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "id": <int>
}
```
Success Return 

```json
{
    "success": true,
    "description": "plan deleted",
    "data": {}
}
```

### List Leaderboard

Method: POST 

Path: /api/deleteplan

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "count": <int>
}
```
Success Return 

```json
{
    "success": true,
    "description": "The Leaderboard got listed",
    "data": {
        "leaderboard": <list>[{
            "rank": <int>,
            "username": <str>,
            "score": <int>,
            "speed": <int>,
            "intensity": <int>,
            "cleanliness": <int>
        }]
    }
}
```

### Get Achievements

Method: GET 

Path: /api/getachievements

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
}
```
Success Return 

```json
{
    "success": true,
    "description": "Returning achievements",
    "data": {
        "achievements": <list>[{
                "name": <str>,
                "title": <str>,
                "description": <str>,
                "level": <int>,
                "progress": <str>,
                "hidden": <bool>,
                "icon": <str>
        }],
        "number_of_unachieved_hiden": <int>
    }
}
```

### Load Friend Achievement

Method: GET 

Path: /api/loadfriendachievements

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
}
```
Success Return 

```json
{
    "success": true,
    "description": "new achieved",
    "data": {
        "achievements": <list>[{
                "name": <str>,
                "title": <str>,
                "description": <str>,
                "level": <int>,
                "progress": <str>,
                "hidden": <bool>,
                "icon": <str>
        }]
    }
}
{
    "success": true,
    "description": "Not achieved",
    "data": {}
}
```

### Load Exercise Achievements

Method: GET 

Path: /api/loadexerciseachievement

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
}
```
Success Return 

```json
{
    "success": true,
    "description": "new achieved",
    "data": {
        "achievements": <list>[{
                "name": <str>,
                "title": <str>,
                "description": <str>,
                "level": <int>,
                "progress": <str>,
                "hidden": <bool>,
                "icon": <str>
        }]
    }
}
{
    "success": true,
    "description": "Not achieved",
    "data": {}
}
```

### Get Medals

Method: GET 

Path: /api/getmedals

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
}
```
Success Return 

```json
{
    "success": true,
    "description": "returning medals",
    "data": {
        "achievements": <list>[{
                "exercise": <str>,
                "gold": <int>,
                "silver": <int>,
                "bronze": <int>
        }]
    }
}
```

### Get Friends

Method: GET 

Path: /api/getfriends

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
}
```
Success Return 

```json
{
    "success": true,
    "description": "returning friends",
    "data": {
        "friends": <list>[{
                "id": <int>,
                "friend1": <str>,
                "friend2": <str>
        }]
    }
}
```

### Get Pending Friendrequests

Method: GET 

Path: /api/getpendingfriendrequests

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
}
```
Success Return 

```json
{
    "success": true,
    "description": "returning pending requests",
    "data": {
        "friends": <list>[{
                "id": <int>,
                "friend1": <str>,
                "friend2": <str>
        }]
    }
}
```

### Get Friendrequests

Method: GET 

Path: /api/getfriendrequests

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
}
```
Success Return 

```json
{
    "success": true,
    "description": "returning requests",
    "data": {
        "friends": <list>[{
                "id": <int>,
                "friend1": <str>,
                "friend2": <str>
        }]
    }
}
```

### Add Friend

Method: POST 

Path: /api/addfriend

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "username": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Request sent",
    "data": {}
}
```

### Accept Friendrequest

Method: POST 

Path: /api/acceptfriendrequest

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "id": <int>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Request accepted",
    "data": {}
}
```

### Decline Friendrequest

Method: POST 

Path: /api/declinefriendrequest

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "id": <int>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Request declined",
    "data": {}
}
```

### Remove Friend

Method: POST 

Path: /api/removefriend

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "id": <int>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Removed friend",
    "data": {
        "removed_friend": <str>
    }
}
```

### Get Profile of Friend

Method: POST 

Path: /api/getprofileoffriend

Header:
```json
{
    "Session-Token": <str>
}
```

Parameters: 
```json
{
    "username": <str>
}
```
Success Return 

```json
{
    "success": true,
    "description": "Returning profile",
    "data": {
        "username": <str>,
        "level": <str>,
        "level_progress": <str>,
        "avatar": <str>,
        "motivation": <str>,
        "last_login": <str>,
        "days": <str>,
        "flame_height": <str>,
        "last_achievements": <list>[{
            "name": <str>,
            "icon": <str>
        }]
    }
}
```