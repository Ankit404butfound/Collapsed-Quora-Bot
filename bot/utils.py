import re 
from quora import User
async def get_answer_count(username_or_link):
    user = User(extract_quora_username(username_or_link))
    profile = await user.profile()
    return profile.answerCount

def extract_quora_username(text):
    pattern = r"(http://|https://|)(www.|)(quora.com/profile/|)([A-Za-z0-9\-]+)/?(.*)"
    match = re.match(pattern, text)
    if match is None:
        return None
    else:
        return match.group(4)
