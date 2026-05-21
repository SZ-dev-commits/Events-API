import requests
import time

# The main URL where the API is running
BASE_URL = "http://127.0.0.1:5000"


def test_api_health_check():
    # Verify if the health endpoint is working
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    assert "healthy" in response.text


def test_user_registration():
    # Create a new user with a unique name using timestamp
    username = f"tester_{int(time.time())}"
    user_data = {"username": username, "password": "pw123"}

    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)

    # Check if the user was successfully created
    assert response.status_code == 201
    assert username in response.text


def test_user_login():
    # 1. Register a temporary user
    temp_user = f"login_test_{int(time.time())}"
    credentials = {"username": temp_user, "password": "pw123"}
    requests.post(f"{BASE_URL}/api/auth/register", json=credentials)

    # 2. Try to log in
    response = requests.post(f"{BASE_URL}/api/auth/login", json=credentials)

    # Check if we get the login token back
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_all_events():
    # Check if the events list can be fetched
    response = requests.get(f"{BASE_URL}/api/events")
    assert response.status_code == 200
    # The result should be a list of events
    assert isinstance(response.json(), list)


def test_prevent_duplicate_registration():
    # Try to register the same username twice
    duplicate_name = "test_user_already_exists"
    user_data = {"username": duplicate_name, "password": "pw123"}

    # First time: success
    requests.post(f"{BASE_URL}/api/auth/register", json=user_data)

    # Second time: should fail (not 201)
    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    assert response.status_code != 201


def test_login_with_invalid_password():
    # Attempt to login with the wrong password
    bad_data = {"username": "admin", "password": "wrong_password_here"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=bad_data)
    assert response.status_code == 401


def test_create_event_without_auth_fails():
    # Trying to create an event without the JWT token
    event_payload = {"title": "Restricted Event", "description": "No access"}
    response = requests.post(f"{BASE_URL}/api/events", json=event_payload)
    # Should return unauthorized status
    assert response.status_code == 401


def test_full_event_creation_process():
    # Step 1: Create and login a user to get a token
    user_name = f"organizer_{int(time.time())}"
    user_pass = "secure_pass"
    requests.post(f"{BASE_URL}/api/auth/register", json={"username": user_name, "password": user_pass})

    login_info = requests.post(f"{BASE_URL}/api/auth/login", json={"username": user_name, "password": user_pass}).json()
    auth_token = login_info["access_token"]

    # Step 2: Create an event using the token
    headers = {"Authorization": f"Bearer {auth_token}"}
    event_body = {
        "title": "Forest Party",
        "description": "Make fun",
        "date": "2025-05-20 18:00:00",
        "location": "South Forest",
        "is_public": True
    }
    response = requests.post(f"{BASE_URL}/api/events", json=event_body, headers=headers)
    assert response.status_code == 201


def test_rsvp_to_existing_event():
    # Step 1: Login a guest user
    guest_name = f"guest_{int(time.time())}"
    requests.post(f"{BASE_URL}/api/auth/register", json={"username": guest_name, "password": "pw"})
    token_data = requests.post(f"{BASE_URL}/api/auth/login", json={"username": guest_name, "password": "pw"}).json()
    auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    # Step 2: Get any available event ID
    events = requests.get(f"{BASE_URL}/api/events").json()
    if len(events) > 0:
        event_id = events[0]["id"]
        # Step 3: Send RSVP
        response = requests.post(f"{BASE_URL}/api/rsvps/event/{event_id}", headers=auth_headers, json={})
        assert response.status_code in [200, 201]


def test_api_root_endpoint():
    # Check if the home page of the API works
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "version" in response.text
