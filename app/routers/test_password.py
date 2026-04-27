import subprocess

def java_chek(password):
    result = subprocess.run(['java', '-jar', 'PasswordStrength.jar', password], capture_output=True, text=True)
    return result.stdout.strip()

