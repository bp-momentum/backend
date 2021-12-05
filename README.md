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
{
}
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

Path: /api/logoutdevices

Header:
```json
{
}
```

Parameters: 
```json
{
    "refresh-token": <str>
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