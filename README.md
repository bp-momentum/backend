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
        "session_token": session_token,
        "refresh_token": refresh_token
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
    "data": {}
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
}
```
Success Return 

```json
{
    "success": true,
    "description": 'user is now logged in',
    "data": {
        "session_token": session_token,
        "refresh-token": refresh_token
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