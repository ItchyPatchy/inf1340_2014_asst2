#!/usr/bin/env python3

""" Computer-based immigration office for Kanadia """

__author__ = 'Susan Sim'
__email__ = "ses@drsusansim.org"

__copyright__ = "2014 Susan Sim"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line
import re
import datetime
import json


def decide(input_file, watchlist_file, countries_file):
    """
    Decides whether a traveller's entry into Kanadia should be accepted

    :param input_file: The name of a JSON formatted file that contains cases to decide
    :param watchlist_file: The name of a JSON formatted file that contains names and passport numbers on a watchlist
    :param countries_file: The name of a JSON formatted file that contains country data, such as whether
        an entry or transit visa is required, and whether there is currently a medical advisory
    :return: List of strings. Possible values of strings are: "Accept", "Reject", "Secondary", and "Quarantine"
    """
    json_input = json.loads(input_file.read())
    json_watchlist = json.loads(watchlist_file.read())
    json_countries = json.loads(countries_file.read())
    return_list = []

    for person in json_input:
        try:
            if json_countries[person["from"]["country"].upper()]["medical_advisory"] != "":
                return_list.append("Quarantine")
                continue
        except KeyError:
            return_list.append("Reject")
            continue
        try:
            if json_countries[person["via"]["country"]]["medical_advisory"] != "":
                return_list.append("Quarantine")
                continue
        except KeyError:

        if not (valid_passport_format(person["passport"]) & valid_date_format(person["birth_date"])):
            return_list.append("Reject")
            continue






            person["first_name"]
            person["last_name"]
            person["passport"]
            person["birth_date"]
            person["home"]
            person["from"]

    return ["Reject"]


def valid_passport_format(passport_number):
    """
    Checks whether a pasport number is five sets of five alpha-number characters separated by dashes
    :param passport_number: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('.{5}-.{5}-.{5}-.{5}-.{5}')

    if passport_format.match(passport_number):
        return True
    else:
        return False


def valid_date_format(date_string):
    """
    Checks whether a date has the format YYYY-mm-dd in numbers
    :param date_string: date to be checked
    :return: Boolean True if the format is valid, False otherwise
    """
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
