# Campaign Management Platform

A backend REST API for managing campaigns, users, campaign members, and campaign-related activities.

This project is being developed progressively according to the project requirements. At the current stage, **Lessons 1, 2, and 3** have been completed.

## Current Progress

| Lesson   | Content                                                    | Status      |
| -------- | ---------------------------------------------------------- | ----------- |
| Lesson 1 | Project structure, database models, schemas, relationships | Completed   |
| Lesson 2 | Authentication, JWT, password hashing, user management     | Completed   |
| Lesson 3 | Campaign management and campaign members                   | Completed   |
| Lesson 4 | Campaign tasks, comments, attachments                      | Not started |

---

## Features

### Authentication

* User registration
* User login
* JWT access tokens
* JWT refresh tokens
* Password hashing with bcrypt
* Access token validation
* Active/inactive account checking
* User roles: `USER` and `ADMIN`

### User Management

* Get current user's profile
* Admin-only user listing/search
* User account status management

### Campaign Management

* Create campaigns
* List campaigns belonging to the current user
* View campaign details
* Update campaigns
* Soft-delete campaigns
* Campaign ownership validation

### Campaign Members

* Automatically add the campaign owner as a campaign member
* Add members to a campaign
* List campaign members
* Remove campaign members
* Member role management
* Owner/member permission checking

### Activity Logging

Important campaign actions are recorded in `activity_logs`, including:

* Campaign creation
* Campaign updates
* Member additions
* Member removals

---

## Tech Stack

* **Python**
* **FastAPI**
* **SQLAlchemy**
* **Pydantic**
* **MySQL**
* **PyJWT**
* **bcrypt**

---

## Project Structure

```text
campaign_management/
│
└── app
    │   main.py
    │   
    ├───core
    │   │   config.py
    │   │   security.py
    │   │   __init__.py
    │  
    │   
    │           
    ├───db
    │   │   database.py
    │   │   __init__.py
    │   │   
    │   └───__pycache__
    │           database.cpython-314.pyc
    │           __init__.cpython-314.pyc
    │           
    ├───dependencies
    │   │   auth.py
    │   │   role.py
    │   │  __init__.py
    │  
    │           
    ├───models
    │   │   campaign.py
    │   │   campaign_task.py
    │   │   user.py
    │   │   __init__.py
    │   
    │           
    ├───routers
    │   │   auth.py
    │   │   campaign.py
    │   │   users.py
    │
    │           
    ├───schemas
    │   │   auth.py
    │   │   campaign.py
    │   │   campaign_task.py
    │   │   response.py
    │   │   user.py
    │   │   __init__.py
    |
    │           
    ├───services
    │   │   auth.py
    │   │   campaign.py
    │   │   user.py
    │   
    │           
    ├───utils
    │   │   exceptions.py
    │   │   rate_limit.py
    
```

---

## Database Design

The current database contains the following main tables:

### `users`

Stores user accounts and authentication information.

Important fields:

* `id`
* `email`
* `password`
* `full_name`
* `role`
* `is_active`
* `created_at`

### `campaigns`

Stores campaign information.

Important fields:

* `id`
* `name`
* `description`
* `owner_id`
* `created_at`
* `deleted_at`

`deleted_at` is used for **soft deletion**.

### `campaign_members`

Represents the relationship between users and campaigns.

Important fields:

* `campaign_id`
* `user_id`
* `role`
* `joined_at`

The combination of `campaign_id` and `user_id` is unique.

Available campaign member roles:

```text
OWNER
MEMBER
```

When a campaign is created, its owner is automatically inserted into `campaign_members` with the `OWNER` role.

### `activity_logs`

Stores important campaign activities.

Important fields:

* `id`
* `campaign_id`
* `user_id`
* `action`
* `created_at`

---

## API Endpoints

### Authentication

| Method | Endpoint         | Description                  |
| ------ | ---------------- | ---------------------------- |
| POST   | `/auth/register` | Register a new user          |
| POST   | `/auth/login`    | Login and receive JWT tokens |
| POST   | `/auth/refresh`  | Generate a new access token  |

### Users

| Method | Endpoint    | Permission | Description                |
| ------ | ----------- | ---------- | -------------------------- |
| GET    | `/users/me` | User       | Get current user's profile |
| GET    | `/users`    | Admin      | List/search users          |

### Campaigns

| Method | Endpoint                   | Permission | Description            |
| ------ | -------------------------- | ---------- | ---------------------- |
| POST   | `/campaigns`               | User       | Create a campaign      |
| GET    | `/campaigns`               | User       | List my campaigns      |
| GET    | `/campaigns/{campaign_id}` | Member     | Get campaign details   |
| PATCH  | `/campaigns/{campaign_id}` | Owner      | Update a campaign      |
| DELETE | `/campaigns/{campaign_id}` | Owner      | Soft-delete a campaign |

### Campaign Members

| Method | Endpoint                                     | Permission | Description           |
| ------ | -------------------------------------------- | ---------- | --------------------- |
| POST   | `/campaigns/{campaign_id}/members`           | Owner      | Add a member          |
| GET    | `/campaigns/{campaign_id}/members`           | Member     | List campaign members |
| DELETE | `/campaigns/{campaign_id}/members/{user_id}` | Owner      | Remove a member       |

---

## Authentication Flow

The application uses JWT-based authentication.

### Login

```text
User
 │
 ▼
POST /auth/login
 │
 ▼
Verify email + password
 │
 ▼
Generate access token
Generate refresh token
 │
 ▼
Return tokens
```

### Accessing a Protected Endpoint

```text
Client
 │
 │ Authorization: Bearer <access_token>
 ▼
get_current_user()
 │
 ├── Decode JWT
 ├── Verify token type
 ├── Verify expiration
 ├── Get user from database
 └── Check account status
 │
 ▼
Protected endpoint
```

### Refresh Token

A refresh token is a separate JWT containing:

```text
sub  → user ID
type → refresh
exp  → expiration time
```

It is used to obtain a new access token without requiring the user to log in again.

---

## Permission Model

Campaign permissions are based on the relationship between the current user and the campaign.

### User

Any authenticated user can:

* Create a campaign
* View their campaigns

### Campaign Member

A campaign member can:

* View campaign details
* View the campaign's member list

### Campaign Owner

The campaign owner can:

* Update the campaign
* Delete the campaign
* Add members
* Remove members

The owner is also stored in `campaign_members` with:

```text
role = OWNER
```

This allows the campaign membership table to represent the complete membership of a campaign.

---

## Service and Dependency Responsibilities

The project separates common authentication logic from campaign-specific business logic.

### Dependencies

`dependencies/` contains reusable system-level dependency logic, such as:

```text
get_current_user()
```

Its responsibility is to identify and authenticate the current user.

### Services

`services/` contains business logic related to specific application features.

For example:

```text
require_campaign_member()
require_campaign_owner()
create_campaign()
get_campaigns()
add_campaign_member()
remove_campaign_member()
```

This keeps the routers relatively simple and makes campaign rules centralized inside the campaign service.

---

## Soft Delete

Campaign deletion currently uses soft deletion.

Instead of physically removing the campaign:

```python
campaign.deleted_at = datetime.now(timezone.utc)
```

The campaign remains in the database but is treated as deleted.

Queries for active campaigns therefore check:

```python
Campaign.deleted_at.is_(None)
```

---

## Running the Project

From the project root:

```bash
uvicorn app.main:app --reload
```

The API will then be available through the configured local server.

FastAPI's interactive documentation can be accessed through:

```text
/docs
```

---

## Development Status

### Completed

* [x] Database configuration
* [x] SQLAlchemy models
* [x] Model relationships
* [x] Pydantic schemas
* [x] User registration
* [x] Login
* [x] Password hashing
* [x] JWT access tokens
* [x] JWT refresh tokens
* [x] Authentication dependency
* [x] User management
* [x] Campaign CRUD
* [x] Campaign ownership
* [x] Campaign membership
* [x] Member permissions
* [x] Soft deletion
* [x] Activity logging

### Upcoming

* [ ] Campaign task management
* [ ] Task permissions
* [ ] Task filtering/search
* [ ] Comments
* [ ] Attachments
* [ ] Additional optional features

---

## Project Goal

The goal of this project is to build a clean and maintainable campaign management backend while progressively implementing the required features.

The implementation intentionally favors **simple, requirement-driven architecture** over unnecessary complexity.
