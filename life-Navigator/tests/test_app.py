import json
import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from app import app  # noqa: E402


class HospitalAllocationAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True)
        cls.client = app.test_client()

    def test_homepage_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"MedRoute AI", response.data)

    def test_state_lookup_returns_known_state(self):
        response = self.client.get("/states")
        self.assertEqual(response.status_code, 200)
        states = response.get_json()
        self.assertIn("maharashtra", states)

    def test_city_lookup_returns_known_city(self):
        response = self.client.get("/cities?q=mu")
        self.assertEqual(response.status_code, 200)
        cities = response.get_json()
        self.assertIn("mumbai", cities)

    def test_allocate_valid_city_renders_results(self):
        response = self.client.post(
            "/allocate",
            data={"city": "mumbai", "emergency": "Cardiac", "severity": "4"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hospital recommendations for Cardiac care", response.data)
        self.assertIn(b"Score breakdown", response.data)

    def test_allocate_invalid_city_renders_friendly_error(self):
        response = self.client.post(
            "/allocate",
            data={"city": "notarealcity", "emergency": "General", "severity": "2"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"We could not produce a ranked hospital list.", response.data)

    def test_chat_returns_context_aware_reply(self):
        response = self.client.post(
            "/chat?hospital=Test+Hospital&icu_load=48&icu_beds=12&severity=High"
            "&emergency=Cardiac&hospital_level=Tertiary&score=91&city=Mumbai"
            "&confidence=High+confidence&reason=ICU+capacity+is+available",
            data=json.dumps({"message": "How strong is this match?"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("high confidence", payload["reply"].lower())


if __name__ == "__main__":
    unittest.main()
