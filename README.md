# backend-task
Backend assignment for the Kuvaka hiring process
# Backend Engineer Hiring Assignment

This is a backend service for lead qualification, built with Flask and integrated with the OpenAI API.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo.git](https://github.com/your-username/your-repo.git)
    cd your-repo
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure API Key:**
    Create a `.env` file in the project root and add your OpenAI API key:
    ```
    OPENAI_API_KEY=your_api_key_here
    ```
5.  **Run the application:**
    ```bash
    flask run
    ```
    The server will run on `http://127.0.0.1:5000`.

## API Usage Examples

You can use `curl` or a tool like Postman/Insomnia to interact with the API.

### 1. Set Product/Offer Details

**`POST /offer`**

This endpoint accepts a JSON payload describing the product.

```bash
curl -X POST [http://127.0.0.1:5000/offer](http://127.0.0.1:5000/offer) \
-H "Content-Type: application/json" \
-d '{"name": "AI Outreach Automation", "value_props": ["24/7 outreach", "6x more meetings"], "ideal_use_cases": ["B2B SaaS mid-market"]}'
