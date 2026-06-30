import os
import subprocess
import sys
import time
import signal

# Track child processes for clean termination
processes = []

def cleanup_and_exit(exit_code):
    print(f"[SUPERVISOR] Shutting down child processes (exit code {exit_code})...")
    for proc in processes:
        if proc.poll() is None:
            try:
                proc.terminate()
            except Exception as e:
                print(f"[SUPERVISOR] Error terminating process: {e}")
    
    # Give them a second to clean up
    time.sleep(1)
    
    for proc in processes:
        if proc.poll() is None:
            try:
                proc.kill()
            except Exception as e:
                print(f"[SUPERVISOR] Error killing process: {e}")
    
    print("[SUPERVISOR] Shutdown complete.")
    sys.exit(exit_code)

def signal_handler(sig, frame):
    print(f"[SUPERVISOR] Received signal {sig}.")
    cleanup_and_exit(0)

# Register signal handlers for clean container shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    port = os.getenv("PORT", "8080")
    print(f"[SUPERVISOR] Starting LLM Cost Autopilot Gateway with reverse proxy on port {port}")

    # Generate nginx configuration targeting the assigned PORT
    nginx_conf_template = """
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    client_body_temp_path /tmp/client_temp;
    proxy_temp_path       /tmp/proxy_temp_path;
    fastcgi_temp_path     /tmp/fastcgi_temp;
    uwsgi_temp_path       /tmp/uwsgi_temp;
    scgi_temp_path        /tmp/scgi_temp;

    sendfile        on;
    keepalive_timeout  65;

    # Stream all logs directly to stdout/stderr for Docker/Railway collection
    access_log /dev/stdout;
    error_log /dev/stderr info;

    server {
        listen {PORT};

        # FastAPI backend router endpoints
        location /v1 {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /docs {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /openapi.json {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Streamlit dashboard and websockets
        location / {
            proxy_pass http://127.0.0.1:8501;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Streamlit websocket config
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }
    }
}
"""
    nginx_conf = nginx_conf_template.replace("{PORT}", port)
    
    conf_path = "/tmp/nginx.conf"
    with open(conf_path, "w") as f:
        f.write(nginx_conf)
    print(f"[SUPERVISOR] Dynamic Nginx configuration written to {conf_path}")

    # Prepare environment with PYTHONPATH set to the workspace root
    env = os.environ.copy()
    cwd = os.getcwd()
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{cwd}:{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = cwd

    # Start FastAPI (Uvicorn)
    print("[SUPERVISOR] Launching FastAPI backend on 127.0.0.1:8000...")
    fastapi_proc = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        env=env
    )
    processes.append(fastapi_proc)

    # Start Streamlit
    print("[SUPERVISOR] Launching Streamlit dashboard on 127.0.0.1:8501...")
    streamlit_proc = subprocess.Popen(
        [
            "streamlit", "run", "dashboard/dashboard.py",
            "--server.port", "8501",
            "--server.address", "127.0.0.1",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ],
        env=env
    )
    processes.append(streamlit_proc)

    # Start Nginx in foreground mode
    print(f"[SUPERVISOR] Launching Nginx reverse proxy on port {port}...")
    nginx_proc = subprocess.Popen(
        ["nginx", "-c", conf_path, "-g", "daemon off; pid /tmp/nginx.pid;"]
    )
    processes.append(nginx_proc)

    # Monitor processes
    print("[SUPERVISOR] All processes running. Monitoring active status...")
    try:
        while True:
            if fastapi_proc.poll() is not None:
                print(f"[SUPERVISOR] FastAPI backend exited unexpectedly with code {fastapi_proc.returncode}")
                break
            if streamlit_proc.poll() is not None:
                print(f"[SUPERVISOR] Streamlit frontend exited unexpectedly with code {streamlit_proc.returncode}")
                break
            if nginx_proc.poll() is not None:
                print(f"[SUPERVISOR] Nginx proxy exited unexpectedly with code {nginx_proc.returncode}")
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print("[SUPERVISOR] KeyboardInterrupt received. Shutting down...")
        cleanup_and_exit(0)
    
    # Trigger cleanup if any monitored process terminates unexpectedly
    cleanup_and_exit(1)

if __name__ == "__main__":
    main()
