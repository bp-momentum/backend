# BP-backend

API Docs



## Create User and Trainer

Type: POST 

Path: /api/createuser

Header:
```json
{
    "session_token": <str>
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
    "session_token": <str>
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

## Get exercise
Type: GET 

Path: /api/getexercise

Header:
```json
{
    "session_token": <str>
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
    "session_token": <str>
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
        "exercise_list": <list>
    }
}
```


## Logout all devices

Type: POST 

Path: /api/logoutdevices

Header:
```json
{
    "session_token": <str>
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

## Delete User

Type: POST 

Path: /api/deleteuser

Header:
```json
{
    "session_token": <str>
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

## Create plan

Type: POST 

Path: /api/createplan

Header:
```json
{
    "session_token": <str>
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
    "user": <str>
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
```json
{
    "success": true,
    "description": 'plan was created but could not be assigned to user',
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
    "session_token": <str>
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