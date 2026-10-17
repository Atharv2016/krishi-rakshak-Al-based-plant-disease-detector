import io
import sys
import unittest
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
import app as krishi_app

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = krishi_app.app.test_client()

    def test_health_shape(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn('status', payload)
        self.assertIn('model_ready', payload)

    def test_predict_requires_image(self):
        response = self.client.post('/api/predict', data={})
        self.assertEqual(response.status_code, 400)

    def test_predict_rejects_wrong_extension(self):
        response = self.client.post('/api/predict', data={'image': (io.BytesIO(b'abc'), 'leaf.gif')}, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)

    def test_predict_rejects_invalid_image(self):
        response = self.client.post('/api/predict', data={'image': (io.BytesIO(b'not-an-image'), 'leaf.jpg')}, content_type='multipart/form-data')
        # If model files are absent, API checks model readiness before decoding. Both responses are safe.
        self.assertIn(response.status_code, (400, 503))

if __name__ == '__main__':
    unittest.main()
