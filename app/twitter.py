import oauth2 as oauth,json
def tweets(username, key="781972478-JRoXuij90DemRjeKdlSHN8jNMYLzJNvo8jfc1jMJ", secret="JeEAviFNXvZ0lZaOoW2qtKNtUp1XJTCfwXNnOOyC8armq", http_method="GET", post_body=None, http_headers=None):
    url="https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name="+username
    consumer = oauth.Consumer(key="RYU42FFuqixnVfuqYUXjqRtAc", secret="OlI3bCBYDDv6WHPMngC0YlxlFaNGwLZXpVYqYu3DggrbLcxyBZ")
    token = oauth.Token(key=key, secret=secret)
    client = oauth.Client(consumer, token)
    resp, content = client.request( url )
    return json.loads(content)
