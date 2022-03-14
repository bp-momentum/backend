# BP-backend

API Docs



## Create User and Trainer

Type: POST 

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

## Login

Type: POST 

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

## Register

Type: POST 

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

## Logout all devices

Type: POST 

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
    "description": 'refresh-token changed',
    "data": {
        "refresh-token": <str>,
        "session_token": <str>
    }
}
```

## Login via refresh-token

Type: POST 

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
    "description": 'user is now logged in',
    "data": {
        "session_token": <str>,
        "refresh-token": <str>
        }
}
```

## Delete Account

Type: POST 

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

## Change Language

Type: POST 

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

## Get Language

Type: GET 

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

## Get Users of Trainer

Type: GET (as trainer) or POST as admin 

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
            "last_login": <string>
        }]
    }
}
```

## Get Trainers

Type: GET

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
            "last_login": <string>
        }]
    }
}
```

## Delete Trainer

Type: POST

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

## Delete User

Type: POST

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

## Get User Level

Type: GET

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

## Get Invited User

Type: GET

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

## Invalidate Invite

Type: POST

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

## Change Username

Type: POST

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

## Change Password

Type: POST

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

## Change Avatar

Type: POST

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

## Change Motivation

Type: POST

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

## Get Profil

Type: GET

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

## Get Trainer Contact

Type: GET

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

## Set Trainer Location

Type: POST

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

## Set Trainer Telephone Number

Type: POST

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

## Set Trainer Academia

Type: POST

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

## Search User

Type: POST

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

## Get List of Users

Type: GET

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

## Get Reset Password Mail

Type: POST

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

## Reset Password

Type: POST

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

## Get exercise

Type: GET 

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
    "description": 'Returned data',
    "data": {
        "title": <str>,
        "description": <str>,
        "video": <str>
    }
}
```

## Get exercise list

Type: GET 

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
    "description": 'list of exercises is provided',
    "data": {
        "exercise_list": <list>[{
                "id": <int>,
                "title": <str>
                }]
    }
}
```


## Get Done Exercise

Type: GET when user else POST

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
    "description": 'Returned list of Exercises and if its done',
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

## Get Done Exercises for month

Type: POST

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
    "description": 'returned plan',
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

## Create plan

Type: POST 

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
    "description": 'plan created',
    "data": {
        "plan_id": plan.id
    }
}
```

## assign plan to user

Type: POST 

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
    "description": 'plan assigned to user',
    "data": {}
}
```

## Get List of Plans
Type: GET 

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
    "description": 'returning all plans',
    "data": {
        'plans': <list>
    }
}
```

## Get Plan

Type: POST 

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
    "description": 'returned plan',
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

## Get Plan of User

Type: POST 

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
    "description": 'returned plan of this account',
    "data": {
            "exercises": <list>
        }
}
```
as trainer:
```json
{
    "success": true,
    "description": 'returned plan of user',
    "data": {
            "exercises": <list>
        }
}
```

## Delete Plan

Type: POST 

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
    "description": 'plan deleted',
    "data": {}
}
```

## List Leaderboard

Type: POST 

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
    "description": 'The Leaderboard got listed',
    "data": {
        "leaderboard": <list>[{"rank": <int>,
                "username": <str>,
                "score": <int>,
                "speed": <int>,
                "intensity": <int>,
                "cleanliness": <int>}]
    }
}
```

## Get Achievements

Type: GET 

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
    "description": 'Returning achievements',
    "data": {
        "achievements": <list>[{"name": <str>,
                "title": <str>,
                "description": <str>,
                "level": <int>,
                "progress": <str>,
                "hidden": <bool>,
                "icon": <str>}],
        "number_of_unachieved_hiden": <int>
    }
}
```

## Load Friend Achievement

Type: GET 

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
    "description": 'new achieved',
    "data": {
        "achievements": <list>[{"name": <str>,
                "title": <str>,
                "description": <str>,
                "level": <int>,
                "progress": <str>,
                "hidden": <bool>,
                "icon": <str>}]
    }
}
{
    "success": true,
    "description": 'Not achieved',
    "data": {}
}
```

## Load Exercise Achievements

Type: GET 

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
    "description": 'new achieved',
    "data": {
        "achievements": <list>[{"name": <str>,
                "title": <str>,
                "description": <str>,
                "level": <int>,
                "progress": <str>,
                "hidden": <bool>,
                "icon": <str>}]
    }
}
{
    "success": true,
    "description": 'Not achieved',
    "data": {}
}
```

## Get Medals

Type: GET 

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
    "description": 'returning medals',
    "data": {
        "achievements": <list>[{"exercise": <str>,
                "gold": <int>,
                "silver": <int>,
                "bronze": <int>}]
    }
}
```

## Get Friends

Type: GET 

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
    "description": 'returning friends',
    "data": {
        "friends": <list>[{"id": <int>,
                "friend1": <str>,
                "friend2": <str>}]
    }
}
```

## Get Pending Friendrequests

Type: GET 

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
    "description": 'returning pending requests',
    "data": {
        "friends": <list>[{"id": <int>,
                "friend1": <str>,
                "friend2": <str>}]
    }
}
```

## Get Friendrequests

Type: GET 

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
    "description": 'returning requests',
    "data": {
        "friends": <list>[{"id": <int>,
                "friend1": <str>,
                "friend2": <str>}]
    }
}
```

## Add Friend

Type: POST 

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
    "description": 'Request sent',
    "data": {}
}
```

## Accept Friendrequest

Type: POST 

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
    "description": 'Request accepted',
    "data": {}
}
```

## Decline Friendrequest

Type: POST 

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
    "description": 'Request declined',
    "data": {}
}
```

## Remove Friend

Type: POST 

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
    "description": 'Removed friend',
    "data": {
        "removed_friend": <str>
    }
}
```

## Get Profile of Friend

Type: POST 

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
    "description": 'Returning profile',
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