import os 
import time 
from slackclient import SlackClient 

BOT_ID = os.environ.get('BOT_ID')

# Constants
AT_BOT = "<@" + BOT_ID + ">"
PYTHON_COMMAND = 'py'

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def parse_slack_output(slack_rtm_output):
	"""
		The Slack Real Time Messaging API is an events firehose.
		This parsing function returns None unless a message is directed to the Bot, based on its ID.
	"""
	output_list = slack_rtm_output
	#print("Output List: %s" % output_list)
	if output_list and len(output_list) > 0:
		for output in output_list:
			if output and 'text' in output and AT_BOT in output['text']:
				# return text after the @ mention, whitespace removed 
				return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
	return None, None 

def handle_command(command, channel):
	"""
		Receives commands directed at the bot and determines if they are valid commands. If so, returns url for the python documentation page with an optional query parameter. 
	"""
	response = "Not sure what you mean. Use the *" + PYTHON_COMMAND + "* command with an optional query to search for inside the documentation page. e.g. \"@doc py string\""

	message = command.split()
	print("Message: %s" % message)

	language = None 
	query = None 
	if len(message) > 1:
		language = message[0].lower()
		query = message[1].lower()
	elif len(message) == 1:
		language = message[0].lower()

	if language == PYTHON_COMMAND:
		if query:
			response = "https://docs.python.org/3/search.html?q=" + str(query)
		else:
			response = "https://docs.python.org/3/"

	# if command.startswith(EXAMPLE_COMMAND):
	# 	response = "https://docs.python.org/3/"
	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


if __name__ == '__main__':
	READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose 
	if slack_client.rtm_connect():
		print('Bot \'doc\' connected and running')
		while True:
			command, channel = parse_slack_output(slack_client.rtm_read())
			if command and channel:
				handle_command(command, channel)
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print('Connnection failed')
