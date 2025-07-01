# BlokID-Backend Assignment
Coding Assignment: Senior Python Developer
Objective
- Design and implement RESTful APIs using FastAPI and PostgreSQL, focusing on user authentication, authorization, and data relationships.

Technology Stack
- **FastAPI**: For building the API.
- **PostgreSQL**: As the database.
- **SQLAlchemy**: For database interaction (ORM).
- **Pytest**: For testing (optional, but recommended).

Boilerplate
- A basic FastAPI project is provided with the following structure:
	- [Boilerplate Repository](<insert-link-to-repo>) (Follow the `README.md` to run the project locally)
	- Project structure:
		```
		project/
		├── app/
		│   ├── models/       # Database models (SQLAlchemy)
		│   ├── schemas/      # Pydantic schemas for request/response validation
		│   ├── routes/       # API routes (FastAPI)
		│   ├── main.py       # Main application file
		│   └── ...           # Other necessary files (e.g., database connection)
		├── requirements.txt  # Project dependencies
		└── ...
		```

Task
- Implement CRUD (Create, Read, Update, Delete) APIs for the following resources, focusing on user authentication, authorization, and relationships:

Users
- **Registration**: Allow users to register with email and password.
- **Login**: Implement user authentication (e.g., using JWT).
- **Email Verification**: Implement email verification for new users.

Organizations
- **Automatic Creation**: When a user registers, automatically create a new organization and assign the user as the organization admin.
- **CRUD Operations**: Allow organization admins to perform CRUD operations on organizations.

Websites
- **CRUD Operations**: Allow organization members to perform CRUD operations on websites within their organization, based on their roles.
- **Association**: Associate websites with organizations (one-to-many relationship).

User Roles and Permissions
- **After Registration**:
	- A new organization is created, and the user is assigned as the **Organization Admin**.
- **Organization Level**:
	- **Organization Admin**:
		- Full access to the organization and its websites.
		- Can invite users to the organization with different roles.
		- **Permissions**:
			- **Organization**: CRUD operations.
			- **Websites**: CRUD operations, invite website members.
	- **Organization User**:
		- Limited access to the organization and its websites.
		- **Permissions**:
			- **Organization**: Read and update operations.
			- **Websites**: Read, create, and update operations.
- **Website Level**:
	- **Website Admin**:
		- Can perform CRUD operations on the website and invite users with website-level access.
		- **Permissions**:
			- **Website**: CRUD operations, invite website members.
	- **Website User**:
		- Can read and update the website.
		- **Permissions**:
			- **Website**: Read and update operations.

Requirements
- **API Design**: Design clear and concise RESTful API endpoints with proper HTTP methods (GET, POST, PUT, DELETE) and status codes.
- **Data Validation**: Use Pydantic schemas to validate request and response data.
- **Authentication**: Implement secure authentication (e.g., JWT) for all endpoints that require it.
- **Authorization**: Enforce proper authorization based on user roles and permissions.
- **Database Relationships**: Implement the database schema with appropriate relationships between users, organizations, and websites.
- **Error Handling**: Handle potential errors gracefully and return informative error responses.
- **Code Quality**: Write clean, well-documented, and maintainable code.
- **Testing**: Write unit tests to cover the core functionality of your API (optional but highly recommended).

Evaluation Criteria
- **Functionality**: Correctness and completeness of the implemented API endpoints.
- **Code Quality**: Cleanliness, readability, and maintainability of the code.
- **Authentication and Authorization**: Security and effectiveness of the authentication and authorization mechanisms.
- **Database Design**: Efficiency and correctness of the database schema and relationships.
- **Error Handling**: Robustness and informativeness of error handling.
- **Testing**: Thoroughness and effectiveness of unit tests (if provided).

Submission
- Submit your code as a Git repository (e.g., on GitHub, GitLab, Bitbucket).
- Include a `README.md` file with instructions on how to run and test your application.
- Create a branch and assign `aung@blokid.com` as a reviewer.

Timeline
- While the initial estimate is 3 days, take the time needed to complete the assignment thoroughly and to the best of your ability.

Notes
- Focus on demonstrating your understanding of API design, authentication, authorization, and database relationships.
- Use any relevant libraries or tools compatible with the specified tech stack.
- For questions or clarification, contact the reviewer.
- Demonstrate your workflow through proper Git commits and branching to showcase your approach and problem-solving process.

This assignment assesses your skills as a Senior Python Backend Developer. We look forward to reviewing your submission!

## Pre-requisites

- Python 3.11.3
- Linter: **Ruff**
- Formatter: **Black**

## Usage

### Print help

```bash
make
```

### Run the application

```bash
make run
```

#### Using docker-compose

```bash
docker-compose -f ./docker/docker-compose.yml up
```

For development, recommend using one local database between multiple projects.
Before running the application, make sure the volumes are created.

- Volume for Postgres

```bash
docker volume create pgdata
```

- Volume for Redis

```bash
docker volume create redisdata
```

### Database

- Generate new migration file

```bash
make generate-migration
```

- Checkout the migration history

```bash
alembic history
```

- Upgrade to the latest revision

```bash
make upgrade
```

- Downgrade to a specific revision

```bash
alembic downgrade <revision>
```

Or downgrade to the previous revision

```bash
make rollback
```

#### Transaction

Easy using transaction with `Transactional` decorator

```python
from core.db import Transactional

class NewsController(BaseController[News]):
  @Transactional()
  async def seed(self):
    ...
```

### Cache

#### Using decorator

```python
from core.cache import Cache

@Cache.cached(prefix="user", ttl=30 * 24 * 60 * 60)
async foo() {

}
```

#### Using `attempt` method

```python
from core.cache import Cache

@Cache.cached(prefix="user", ttl=30 * 24 * 60 * 60)

async def scrape(url: str) {
  return await fetch(url)
}

async def main() {
  data = await Cache.attempt(
    key="linkedin-scraper",
    ttl=60,
    fn=scrape_linkedin,
    url="https://www.linkedin.com/"
  )
}
```

### Code quality

- **Check format the code**

```bash
make check-format
```

- **Lint the code**

```bash
make lint
```
