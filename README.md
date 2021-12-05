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
    "username": <str>,
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



