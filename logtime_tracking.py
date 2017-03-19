#!/usr/bin/env python
# coding: utf-8

import sys
from ConfigParser import ConfigParser
from sanction import Client
from datetime import datetime, timedelta, date
import json


def get_config():
	config = ConfigParser({}, dict)
	config.read('config.conf')
	c = config._sections['sanction']
	return config._sections['sanction']

def get_range_logtime_two():
	begin = get_date_two("begin")
	end = get_date_two("end")
	if begin > end:
		sys.exit("Begin_date is after end_date ...")
	return begin, end

def get_range_logtime_yesterday():
	begin = get_date_yesterday("begin")
	end = get_date_yesterday("end")
	if begin > end:
		sys.exit("Begin_date is after end_date ...")
	return begin, end

def get_range_logtime_today():
	begin = get_date_today("begin")
	end = get_date_today("end")
	if begin > end:
		sys.exit("Begin_date is after end_date ...")
	return begin, end

def get_date(state):
	now = datetime.now()
	while True:
		print "Date " + state + "? YYYY-MM-DD // empty = today"
		date_input = raw_input()
		if date_input:
			try:
				dt = datetime.strptime(date_input, "%Y-%m-%d")
				if state == "begin":
					return dt
				else:
					return dt + timedelta(days=1)
			except ValueError as e:
				print e
		else:
			if state == "begin":
				return datetime.strptime(str(now.date()), "%Y-%m-%d")
			else:
				return datetime.utcnow()

def get_date_today(state):
	now = datetime.now()
	if state == "begin":
		return datetime.strptime(str(now.date()), "%Y-%m-%d")
	else:
		return datetime.utcnow()

def get_date_yesterday(state):
	now = datetime.now()
	if state == "begin":
		return datetime.strptime(str((now - timedelta(days=1)).date()), "%Y-%m-%d")
	else:
		return datetime.strptime(str((now - timedelta(days=0)).date()), "%Y-%m-%d")

def get_date_two(state):
	now = datetime.now()
	if state == "begin":
		return datetime.strptime(str((now - timedelta(days=2)).date()), "%Y-%m-%d")
	else:
		return datetime.strptime(str((now - timedelta(days=1)).date()), "%Y-%m-%d")

def get_token(grant_type):
	client = Client(token_endpoint = get_config()["42.token_url"],
					resource_endpoint = get_config()["42.endpoint"],
					client_id = get_config()["42.client_id"],
					client_secret = get_config()["42.client_secret"])
	client.request_token(grant_type=grant_type)
	return client


def get_user_id(client, login):
	user_info = client.request("/v2/users?filter[login]=" + login)
	if user_info:
		user_id = user_info[0]['id']
	else:
		sys.exit("User doesn't exist")
	return user_id


def get_logtime(user_locations):
	logtime = timedelta()
	for x in user_locations:
		if x['end_at']:
			log_end = datetime.strptime((x['end_at'])[:19], "%Y-%m-%dT%H:%M:%S")
		else:
			log_end = datetime.strptime((str(datetime.utcnow()))[:19], "%Y-%m-%d %H:%M:%S")
		log_start = datetime.strptime((x['begin_at'])[:19], "%Y-%m-%dT%H:%M:%S")
		log_session = log_end - log_start
		logtime += log_session
	return logtime


def format_output_datetime(duration_timedelta):
	hours, remainder = divmod(duration_timedelta, 3600)
	minutes, seconds = divmod(remainder, 60)
	return (hours, minutes)


def get_more_location(client, request, locations, range_begin):
	tmp = True
	i = 2;
	while tmp:
		last_location = datetime.strptime((locations[-1]['begin_at'])[:10], "%Y-%m-%d")
		if range_begin < last_location:
			tmp = client.request(request + "&page[number]=" + str(i))
			locations += tmp
			i += 1
		else:
			return

def twodaysago():
	client = get_token("client_credentials")
	login = get_config()["42.login"]
	user_id = get_user_id(client, login)
	range_begin, range_end = get_range_logtime_two()
	range_date = "?page[size]=100&range[begin_at]=" + str(range_begin) + "," + str(range_end)
	request = "/v2/users/" + str(user_id) + "/locations" + range_date
	locations = client.request(request)
	if locations:
		get_more_location(client, request, locations, range_begin)
		first_log = (locations[-1]['begin_at'])[:10]
		if locations[0]['end_at']:
			last_log = (locations[0]['end_at'])[:10]
		else:
			last_log = ((str(datetime.utcnow())))[:10]
		logtime = get_logtime(locations)
		(h, m) = format_output_datetime(logtime.days * 86400 + logtime.seconds)
		#print "between:", first_log, range_begin
		#print "    and:", last_log, range_end
		print "2 days ago logtime:" , '%02dh%02d' % (h, m)
	else:
		#print "between:", range_begin
		#print "    and:", range_end
		print "2 days ago logtime not available ..."

def yesterday():
	client = get_token("client_credentials")
	login = get_config()["42.login"]
	user_id = get_user_id(client, login)
	range_begin, range_end = get_range_logtime_yesterday()
	range_date = "?page[size]=100&range[begin_at]=" + str(range_begin) + "," + str(range_end)
	request = "/v2/users/" + str(user_id) + "/locations" + range_date
	locations = client.request(request)
	if locations:
		get_more_location(client, request, locations, range_begin)
		first_log = (locations[-1]['begin_at'])[:10]
		if locations[0]['end_at']:
			last_log = (locations[0]['end_at'])[:10]
		else:
			last_log = ((str(datetime.utcnow())))[:10]
		logtime = get_logtime(locations)
		(h, m) = format_output_datetime(logtime.days * 86400 + logtime.seconds)
		#print "between:", first_log, range_begin
		#print "    and:", last_log, range_end
		print "Yesterday's logtime:" , '%02dh%02d' % (h, m)
	else:
		#print "between:", range_begin
		#print "    and:", range_end
		print "Yesterday's logtime not available ..."

def today():
	client = get_token("client_credentials")
	login = get_config()["42.login"]
	user_id = get_user_id(client, login)
	range_begin, range_end = get_range_logtime_today()
	range_date = "?page[size]=100&range[begin_at]=" + str(range_begin) + "," + str(range_end)
	request = "/v2/users/" + str(user_id) + "/locations" + range_date
	locations = client.request(request)
	if locations:
		get_more_location(client, request, locations, range_begin)
		first_log = (locations[-1]['begin_at'])[:10]
		if locations[0]['end_at']:
			last_log = (locations[0]['end_at'])[:10]
		else:
			last_log = ((str(datetime.utcnow())))[:10]
		logtime = get_logtime(locations)
		(h, m) = format_output_datetime(logtime.days * 86400 + logtime.seconds)
		#print "between:", first_log, range_begin
		#print "    and:", last_log, range_end
		print "Today's logtime:" , '%02dh%02d' % (h, m)
	else:
		#print "between:", range_begin
		#print "    and:", range_end
		print "Today's logtime not available ..."

def main():
	today()
	yesterday()
	twodaysago()

main()
