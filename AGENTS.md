# AWS FASTAPI FOUNDATION PROJECT

## Business plan (MVP)
I want to learn Python backend development of cloud applications.
The app should be a "hello-world" Python and FastAPi based backed app.
The app will be deployed and served from AWS as container based cloud APIs

## Tech Stack
- FastAPI
- Uvicorn
- uv for dependency management
- ruff for lint/format
- pytest for unit testing
- docker for packaging 
- AWS ECR for storing docker images
- AWS ECS and/or Fargate for deployment + Application Load Balancer
- AWS Cloudwatch for logs
- AWS IAM + security groups + VPC/subnets for access control 

## Technical Details

- No persistence
- No user management for the MVP
- Use popular libraries
- As simple as possible but with an elegant UI

## Strategy

1. Write plan with success criteria for each phase to be checked off. Include project scaffolding, including .gitignore, and rigorous unit testing.
2. Execute the plan ensuring all critiera are met
3. Carry out extensive integration testing, fixing defects
4. Only complete when the MVP is finished and tested, with the server running and ready for the user

## Coding standards

1. Use latest versions of libraries and idiomatic approaches as of today
2. Keep it simple - NEVER over-engineer, ALWAYS simplify, NO unnecessary defensive programming. No extra features - focus on simplicity.
3. Be concise. Keep README minimal. IMPORTANT: no emojis ever
4. If something is not working, make sure you fully understand why and demonstrate that the fix works

## Research Before Answering

- When asked about third-party tools, CLIs, or APIs: search docs or source code before answering. Do not rely on memory alone.
- If uncertain, say so explicitly and look it up rather than guessing.
- For configuration options: verify against the actual tool's "--help" output or source before recommending.