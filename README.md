# ASCC
Aviation Safety Coding Challenge

## How to Run

1. Clone the repository
2. Make a copy from `.env.dist` and rename it to `.env`
3. Run `docker compose up`
4. Open your browser and navigate to `http://localhost:4200`


### Some additional information
- The first time the application startup time is a bit longer due to the migration and data seeding process (~30 seconds)
- With the usage of `docker compose up`, the frontend is built and served by a separate container with a two-stage docker build process
- The `http://localhost:4200` loads the prebuilt angular application
- FastAPI docs are available at `http://localhost:4200/docs`
