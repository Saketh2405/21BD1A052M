from fastapi import FastAPI, HTTPException
import httpx
from typing import List, Dict, Any

app = FastAPI()

WINDOW_SIZE = 10
TIMEOUT = 0.5 
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzE3MDc2MDA2LCJpYXQiOjE3MTcwNzU3MDYsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6ImU5NTZhNmMwLTRmOTItNGE3NS05ZTM5LTBlOTE5MzA2M2EwYyIsInN1YiI6InNha2V0aHJlZGR5MjQwNUBnbWFpbC5jb20ifSwiY29tcGFueU5hbWUiOiJhZmZvcmRtZWQiLCJjbGllbnRJRCI6ImU5NTZhNmMwLTRmOTItNGE3NS05ZTM5LTBlOTE5MzA2M2EwYyIsImNsaWVudFNlY3JldCI6IkRZWkRtVGR5WXVhaXRNd3YiLCJvd25lck5hbWUiOiJTYWtldGgyNDA1Iiwib3duZXJFbWFpbCI6InNha2V0aHJlZGR5MjQwNUBnbWFpbC5jb20iLCJyb2xsTm8iOiIyMUJEMUEwNTJNIn0.zB8PMGcxDAEwYIrQJwd3gkiaOJuYIXKTuAW_xNdmay4"  # Replace with your actual auth token

stored_numbers = {
    'p': [],
    'f': [],
    'e': [],
    'r': []
}

NUMBER_ENDPOINTS = {
    'p': "http://20.244.56.144/test/primes",
    'f': "http://20.244.56.144/test/fibo",
    'e': "http://20.244.56.144/test/even",
    'r': "http://20.244.56.144/test/rand"
}

@app.get("/numbers/{number_id}")
async def get_numbers(number_id: str) -> Dict[str, Any]:
    if number_id not in NUMBER_ENDPOINTS:
        raise HTTPException(status_code=400, detail="Invalid number ID")

    previous_state = stored_numbers[number_id][:]
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(NUMBER_ENDPOINTS[number_id], headers=headers)
            response.raise_for_status()
            numbers = response.json().get("numbers", [])
    except (httpx.RequestError, httpx.HTTPStatusError):
        numbers = []
    print(numbers)
    for number in numbers:
        if number not in stored_numbers[number_id]:
            stored_numbers[number_id].append(number)
            if len(stored_numbers[number_id]) > WINDOW_SIZE:
                stored_numbers[number_id].pop(0)

    current_state = stored_numbers[number_id]

    if current_state:
        avg = sum(current_state) / len(current_state)
    else:
        avg = 0.0

    return {
        "windowPrevState": previous_state,
        "windowCurrState": current_state,
        "numbers": numbers,
        "avg": round(avg, 2)
    }

if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0",port=9876)