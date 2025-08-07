import os
import time
import requests
import pytest
import subprocess

@pytest.fixture(scope="session", autouse=True)
def live_server():
    """
    1) Builds the image under test
    2) Spins up a container on 8080
    3) Tears it down when tests are done
    """
    image = "server-one:integration"
    subprocess.run(
        ["docker", "build", "--tag", image, "-f", "apps/server-one/Dockerfile", "."],
        check=True
    )
    container = subprocess.Popen([
        "docker", "run", "--rm", "-p", "8080:8080", image
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

    yield

    container.terminate()
    container.wait()

def test_echo_endpoint(live_server):
    msg = "integration123"
    r = requests.get(f"http://localhost:8080/echo/{msg}")
    assert r.status_code == 200
    assert r.json() == msg

def test_memory_metrics_endpoint(live_server):
    r = requests.get("http://localhost:8080/metrics/memory")
    assert r.status_code == 200
    # should be a float >= 0
    val = float(r.text)
    assert val >= 0