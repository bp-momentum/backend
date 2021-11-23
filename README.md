# BP-backend

API Docs



## Create User and Trainer

Type: POST 

Path: /api/createuser

Parameters: 
```json
{
    "first_name": <str>,
    "last_name": <str>,
    "username": <str>,
    "password": <str>,
    "email_address": <str>,
    "session_token": <str>
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


