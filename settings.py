import os

slacktoken = os.getenv('SLACK_BOT_MLTESTING_TOKEN')
slackchannel = os.getenv('SLACK_BOT_CHANNEL')
s3_file = os.getenv('SLACK_BOT_S3_FILE')
graph_host = os.getenv('SLACK_BOT_GRAPH_HOST')
