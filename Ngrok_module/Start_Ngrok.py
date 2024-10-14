import subprocess

# Start the ngrok process
print("Starting Ngrok")
ngrok_command = ["ngrok", "http", "--hostname=lemming-national-anemone.ngrok-free.app", "7115"]
subprocess.Popen(ngrok_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
