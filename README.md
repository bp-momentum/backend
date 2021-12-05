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
        "access_token": <str>
    }
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
    "date": <list>,
    "sets": <list>,
    "repeats_per_set": <list>,
    "exercise": <list>,
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
