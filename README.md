# Promosee API

This is the API code for the Promosee application. The Promosee API is built using FastAPI, a modern, fast (high-performance) web framework for building APIs with Python. This API also include machine learning model with TensorFlow, Transformers, Pandas, and imblearn.

## Requirements

- Python 3.7 or later
- `pip` package manager

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Bangkit-Capstone-C23-PS338/modul-CC.git
    cd modul-CC
    ```

2. Create a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Set up environment variables:
    - Create a .env file in the root directory of the project.
    - Define the following environment variables in the .env file:
    - CREDENTIALS: The credentials for accessing Google Cloud Firestore.
    - SECRET_KEY: Secret key used for JWT token generation.
    - GOOGLE_APPLICATION_CREDENTIALS: Path to the Google Cloud credentials JSON file.
5. Start the API server:
    ```bash
    uvicorn main:app --reload
    ```
    The API server should now be running at http://localhost:8000

## Data Model
- BusinessOwner: Represents a business owner user.
- Influencer: Represents an influencer user.
- Product: Represents a product.
- Order: Represents an order.
- Review: Represents a review.

## API Endpoints that are used in our app
- @app.post("/register/businessowner")
- @app.post("/register/influencer")
- @app.post("/login")
- @app.put("/update/{username}")
- @app.get("/getinfluencers")
- @app.get("/getinfluencer/{username}")
- @app.post("/influencers/{username}/products")
- @app.put("/influencers/{username}/products/{product_id}")
- @app.delete("/influencers/{username}/products/{product_id}")
- @app.get("/influencers/{username}/products")
- @app.get("/influencers/{username}/products/{product_id}")
- @app.post("/add_influencer_order/{influencer_username}")
- @app.put("/update_order/{order_id}")
- @app.post("/add_influencer_review/{order_id}")
- @app.get("/orders_business_owner/{business_owner}")
- @app.get("/influencer_orders/{influencer}")
- @app.get("/influencer_reviews/{influencer}")
- @app.get("/get_business_owner/{business_owner}")
- @app.get("/get_order_details/{order_id}")
- @app.get("/get_all_business_owners")
- @app.get("/get_BusinessOwner_influencerrank_detail/{business_owner}")
- @app.post("/logout")

## Error Handling

The API returns appropriate HTTP status codes and error messages for different scenarios. Make sure to handle errors gracefully in your client applications.

## API Deployment
- Build Docker Image using Docker from the Dockerfile that has been configured using the tag from Container Registry
- Push the Docker Image into Container Registry that has been set in our Google Cloud
- Deploy the Docker Image in the Container Registry using Cloud Run

## Cloud Run Specification
- Startup CPU Boost Enabled
- 4 vCPUs
- 8 GB memory
- Request Timeout 300s
- Maximum concurrent requests per instance 80
- Container port 8080
