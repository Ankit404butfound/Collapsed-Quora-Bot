# Collapsed-Quora-Bot
This bot will let you know when any of your answers on Quora collapses.

## Working
This uses selenium to get the number of answer an account is having then compare it with previously stored number,
i.e when you register, it stores your Username, chat-id, Quora profile URL and *Number of answers*.
If the previous number was bigger than the current number this means the answer has collapsed, otherwise you have answerd new question,
If they both are equal, you have no activity for that session.
