import random

# pyrefly: ignore [missing-import]
from locust import HttpUser, between, task

QUESTIONS = [
    "Summarize the uploaded document.",
    "What are the main findings?",
    "Explain the methodology.",
    "List the important conclusions.",
    "What does the document discuss?",
]


class EnterpriseRAGUser(HttpUser):

    wait_time = between(1, 3)

    access_token = None
    session_id = None

    def on_start(self):

        # Ensure the user exists before trying to log in
        with self.client.post(
            "/auth/register",
            json={
                "email": "admin@example.com",
                "name": "Admin User",
                "password": "password",
            },
            catch_response=True
        ) as response:
            if response.status_code == 400:
                response.success()  # Ignore "Email already registered" error

        login = self.client.post(
            "/auth/login",
            json={
                "email": "admin@example.com",
                "password": "password",
            },
        )

        login.raise_for_status()

        self.access_token = login.json()["access_token"]

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        session = self.client.post(
            "/chat/sessions",
            headers=headers,
        )

        session.raise_for_status()

        self.session_id = session.json()["session_id"]

    @task
    def chat(self):

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        self.client.post(
            "/chat",
            headers=headers,
            json={
                "session_id": self.session_id,
                "question": random.choice(QUESTIONS),
                "document_ids": [],
            },
            name="/chat",
        )
