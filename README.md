# AIF-helpbot
SlackBot used for Q/A

The server can be run with `python run_debug.py`
It receives the hooks from Slack when the Helpbot, a Slack bot, receives a call from a user.

The bot has a simple tasks :
- When a question is asked, it posts it in another and waits for someone to post an answer
- When someone answers with the question id, it posts the answer in the room where the question was asked

Proper slack token need to be set up in config in order to work
The repo was deployed using https://github.com/AdMoR/AIF-ansible-website
