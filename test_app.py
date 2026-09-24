import subprocess, sys, time, urllib.request, unittest

class HealthCheckTest(unittest.TestCase):
    def test_health_endpoint(self):
        proc = subprocess.Popen([sys.executable, "app.py"])
        time.sleep(1)  # give the server a moment to start listening
        try:
            resp = urllib.request.urlopen("http://localhost:3000/health")
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.read(), b"ok")
        finally:
            proc.terminate()
            proc.wait()  # block until the subprocess has actually exited

if __name__ == "__main__":
    unittest.main()