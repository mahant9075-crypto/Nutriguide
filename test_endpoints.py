import urllib.request
import urllib.parse
import json
import os

BASE_URL = "http://localhost:8000"

def make_request(url, method="GET", data=None):
    try:
        req = urllib.request.Request(url, method=method)
        req.add_header('Content-Type', 'application/json')
        
        if data:
            json_data = json.dumps(data).encode('utf-8')
            req.data = json_data
            
        with urllib.request.urlopen(req) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def test_endpoints():
    print("Testing endpoints...")
    
    # 1. Root
    status, content = make_request(BASE_URL)
    print(f"Root: {status}")

    # 2. Predict
    data = {
        "name": "Test User",
        "age": 55,
        "height": 175,
        "weight": 80,
        "blood_group": "O+",
        "sugar_level": 160
    }
    status, content = make_request(f"{BASE_URL}/predict", "POST", data)
    print(f"Predict: {status}")
    response_json = json.loads(content)
    print(response_json)
    prediction = response_json.get("prediction")

    # 3. Recommend
    if prediction:
        # Encode query param
        safe_prediction = urllib.parse.quote(prediction)
        status, content = make_request(f"{BASE_URL}/recommend?disease={safe_prediction}", "POST")
        print(f"Recommend: {status}")
        print(json.loads(content))

    # 4. Feedback
    feedback = {
        "user_name": "Test User",
        "message": "Testing feedback",
        "contact_info": "test@example.com"
    }
    status, content = make_request(f"{BASE_URL}/feedback", "POST", feedback)
    print(f"Feedback: {status}")
    print(json.loads(content))

    # 5. Report
    status, content = make_request(f"{BASE_URL}/report?prediction={urllib.parse.quote(prediction)}", "POST", data)
    print(f"Report: {status}")
    if status == 200:
        with open("report_test_urllib.pdf", "wb") as f:
            f.write(content)
        print("Report saved to report_test_urllib.pdf")

if __name__ == "__main__":
    test_endpoints()
