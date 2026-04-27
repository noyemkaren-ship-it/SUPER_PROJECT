import subprocess
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def java_chek(password):
    try:
        result = subprocess.run(
            ['java', '-cp', CURRENT_DIR, 'Chek', password],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Собираем ВСЁ
        output = result.stdout.strip()
        error = result.stderr.strip()
        returncode = result.returncode
        
        # Печатаем в консоль FastAPI
        print(f"[JAVA] stdout: '{output}'")
        print(f"[JAVA] stderr: '{error}'")
        print(f"[JAVA] returncode: {returncode}")
        
        if error:
            return f"java_error: {error}"
        if output:
            return output.lower()
        return "empty_output"
    
    except FileNotFoundError:
        print("[JAVA] Java не найдена!")
        return "java_not_found"
    except subprocess.TimeoutExpired:
        print("[JAVA] Превышено время ожидания!")
        return "timeout"
    except Exception as e:
        print(f"[JAVA] Exception: {e}")
        return f"exception: {e}"