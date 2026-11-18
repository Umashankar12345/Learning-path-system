import time
from urllib.parse import quote, urljoin

import requests
from django.conf import settings


class JudgeConfigurationError(Exception):
    pass


class JudgeServiceError(Exception):
    pass


TERMINAL_STATUSES = {
    3: "accepted",
    4: "wrong_answer",
    5: "time_limit",
    6: "compile_error",
    7: "runtime_error",
    8: "runtime_error",
    9: "runtime_error",
    10: "runtime_error",
    11: "runtime_error",
    12: "runtime_error",
    14: "runtime_error",
}


def _judge_headers():
    headers = {"Content-Type": "application/json"}
    api_key = getattr(settings, "JUDGE0_API_KEY", "")
    api_host = getattr(settings, "JUDGE0_API_HOST", "")
    if api_key:
        headers["X-RapidAPI-Key"] = api_key
    if api_host:
        headers["X-RapidAPI-Host"] = api_host
    return headers


def _get_submission_result(base_url, token, headers):
    url = urljoin(base_url.rstrip("/") + "/", f"submissions/{quote(token, safe='')}")
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        try:
            response = requests.get(
                url,
                params={"base64_encoded": "false"},
                headers=headers,
                timeout=(3, 5),
            )
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as exc:
            raise JudgeServiceError("Could not retrieve the Judge0 result.") from exc
        except ValueError as exc:
            raise JudgeServiceError("Judge0 returned an invalid result.") from exc

        if not isinstance(result, dict) or not isinstance(result.get("status"), dict):
            raise JudgeServiceError("Judge0 returned a malformed result.")
        status_id = result["status"].get("id")
        if status_id in TERMINAL_STATUSES:
            result["normalized_status"] = TERMINAL_STATUSES[status_id]
            return result
        if status_id == 13:
            raise JudgeServiceError("Judge0 reported an internal execution error.")
        if status_id != 1 and status_id != 2:
            raise JudgeServiceError("Judge0 returned an unknown submission status.")
        time.sleep(0.3)

    raise JudgeServiceError("Judge0 took too long to execute this test case.")


def run_test_case(*, source_code, language_id, stdin, expected_output):
    base_url = getattr(settings, "JUDGE0_API_URL", "").strip()
    if not base_url:
        raise JudgeConfigurationError(
            "Code judging is not configured. Set JUDGE0_API_URL in the project .env file."
        )

    url = urljoin(base_url.rstrip("/") + "/", "submissions")
    headers = _judge_headers()
    payload = {
        "source_code": source_code,
        "language_id": language_id,
        "stdin": stdin,
        "expected_output": expected_output,
        "cpu_time_limit": 2,
        "wall_time_limit": 5,
        "memory_limit": 128000,
    }

    try:
        response = requests.post(
            url,
            params={"base64_encoded": "false", "wait": "false"},
            json=payload,
            headers=headers,
            timeout=(3, 10),
        )
        response.raise_for_status()
        submission = response.json()
    except requests.RequestException as exc:
        raise JudgeServiceError("Could not submit code to Judge0.") from exc
    except ValueError as exc:
        raise JudgeServiceError("Judge0 returned an invalid submission response.") from exc

    token = submission.get("token")
    if not token:
        raise JudgeServiceError("Judge0 did not return a submission token.")

    result = _get_submission_result(base_url, token, headers)
    return {
        "status": result["normalized_status"],
        "stdout": result.get("stdout") or "",
        "diagnostic": (
            result.get("stderr")
            or result.get("compile_output")
            or result.get("message")
            or ""
        )[:2000],
        "time": result.get("time"),
        "memory": result.get("memory"),
    }
