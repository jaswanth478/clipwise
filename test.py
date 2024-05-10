from lambda_function import lambda_handler

event = {
    "youtube_url": "https://www.youtube.com/watch?v=C7OQHIpDlvA"
}

response = lambda_handler(event)
print(response)
