import urllib3
urllib3.disable_warnings()
import os.path

import json
import requests
import uservoice
import time

from config import *


def send_ticket_to_freshdesk(ticket, ticket_number):
	_url = "https://%s.freshdesk.com/api/v2/tickets" % FD_SUBDOMAIN
	_headers = {
		'Content-Type': 'application/json'
	}
	_data = json.dumps(ticket)

	time.sleep(1) # to prevent rate limit
	r = requests.post(_url, data = _data, auth=(FD_API_KEY, "api"), headers=_headers, verify=False)
	if r.status_code != 200 and r.status_code != 201:
		print('x %s: %s' % (ticket_number, r.text))
		return {}
	else:
		# print('✓ %s' % (ticket_number))
		return r.json()


def process_uv_ticket(uv_ticket):
	ticket = {}
	ticket['status'] = 5
	ticket['priority'] = 1
	ticket['source'] = 2
	ticket['email'] = uv_ticket['contact']['email']
	ticket['name'] = uv_ticket['contact']['name']
	description = "<b>From UserVoice:</b> <a href=\"https://%s.uservoice.com/admin/tickets/%s\">%s</a><br/>" % (
		UV_SUBDOMAIN,
		uv_ticket['ticket_number'],
		uv_ticket['ticket_number']
	)
	for message in uv_ticket['messages'][::-1]:
		if message['is_admin_response']:
			ticket['status'] = 4
		description += (
			"<br/>---<br/>"
			"<b>%s &lt;%s&gt;</b><br/>"
			"%s<br/>"
			"<i>%s</i><br/>"
			"<br/>%s<br/><br/>"
		) % (
			message['sender']['name'],
			message['sender']['email'],
			message['created_at'],
			message['referrer'],
			message['body'],
		)
	ticket['description'] = description
	ticket['subject'] = uv_ticket['subject']
	ticket['tags'] = ['uservoice']

	send_ticket_to_freshdesk(ticket, uv_ticket['ticket_number'])
	
	
def download_uv_tickets(uv_ticket_outfile, total_records):
	'''thanks https://github.com/drmarshall/zendesk_migration'''
	uv_client = uservoice.Client(UV_SUBDOMAIN, UV_API_KEY, UV_API_SECRET)
	base_url = "/api/v1/tickets.json?"
	total_records = total_records
	
	tickets = {}
	page = 1
	print("Downloading page %s" % str(page))
	with open(uv_ticket_outfile, "w") as f:
		while total_records > page*100:
			request = base_url+"page="+str(page)+"&per_page=100"+"&type=Support+Request&state=closed"
			response = uv_client.get(request)
			f.write(json.dumps(response['tickets'])+"\n")
			print(json.dumps(response['response_data']))
			page = response['response_data']['page'] + 1 
			total_records = response['response_data']['total_records']
			print("Downloading page %s of %s pages" % (str(page), str(total_records/100)))


def import_tickets_to_freshdesk(uv_ticket_outfile):
	with open("uservoice_export.json", "r") as uservoice_export:
		batch = 1
		current = 0
		
		tickets = []
		total = 0
		for line in uservoice_export:
			ticket_batch = json.loads(line)
			for ticket in ticket_batch:		
				tickets.append(ticket)
				total += 1

		for ticket in tickets: 
			process_uv_ticket(ticket)
			current += 1
			print("%s/%s" % (current, total))


if __name__ == '__main__':
	uv_ticket_outfile = "uservoice_export.json"
	if not os.path.isfile(uv_ticket_outfile):
		download_uv_tickets(uv_ticket_outfile, total_records=60000)
	import_tickets_to_freshdesk(uv_ticket_outfile)
