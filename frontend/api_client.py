import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def ask_backend(question: str, timeout: int = 60) -> dict:
    """
    يرسل السؤال للـ backend ويرجع dict فيه answer و sources.
    يرفع استثناء واضح لو حصل خطأ اتصال أو استجابة غير متوقعة.
    """
    try:
        r = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question},
            timeout=timeout,
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        raise ConnectionError("تعذر الاتصال بالخادم. تأكد أن الـ backend يعمل على " + API_BASE_URL)
    except requests.exceptions.Timeout:
        raise TimeoutError("استغرق الخادم وقتًا طويلاً للرد. حاول مرة أخرى.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"خطأ من الخادم: {e}")

def check_health(timeout: int = 5) -> bool:
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=timeout)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False