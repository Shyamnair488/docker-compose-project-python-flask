from flask import Flask
import redis
import os

app = Flask(__name__)

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    decode_responses=True
)

@app.route("/")
def home():
    count = r.incr("visits")

    return f"""
    <h1>Welcome to Shyam's Docker Compose!</h1>
    <h2>Flask Application</h2>
    <p>Page Visits: {count}</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
