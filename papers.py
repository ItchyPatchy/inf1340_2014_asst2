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
import os.path


def decide(input_file, watchlist_file, countries_file):
    """
    Decides whether a traveller's entry into Kanadia should be accepted

    :param input_file: The name of a JSON formatted file that contains cases to decide
    :param watchlist_file: The name of a JSON formatted file that contains names and passport numbers on a watchlist
    :param countries_file: The name of a JSON formatted file that contains country data, such as whether
        an entry or transit visa is required, and whether there is currently a medical advisory
    :return: List of strings. Possible values of strings are: "Accept", "Reject", "Secondary", and "Quarantine"
    """
    script_path = os.path.dirname(__file__)
    with open(os.path.join(script_path, input_file)) as file_reader:
        json_input = json.loads(file_reader.read())
    with open(os.path.join(script_path, watchlist_file)) as file_reader:
        json_watchlist = json.loads(file_reader.read())
    with open(os.path.join(script_path, countries_file)) as file_reader:
        json_countries = json.loads(file_reader.read())
    return_list = []

    for person in json_input:
        try:
            if person["from"]["country"].upper() != "KAN":
                if json_countries[person["from"]["country"].upper()]["medical_advisory"] != "":
                    return_list.append("Quarantine")
                    continue
        except KeyError:
            return_list.append("Reject")
            continue

        try:
            if json_countries[person["via"]["country"].upper()]["medical_advisory"] != "":
                return_list.append("Quarantine")
                continue
        except KeyError:
            pass

        try:
            if not (valid_passport_format(person["passport"]) & valid_date_format(person["birth_date"])):
                return_list.append("Reject")
                continue
        except KeyError:
            return_list.append("Reject")
            continue

        try:
            if person["entry_reason"].lower() == "visit":
                if json_countries[person["home"]["country"].upper()]["visitor_visa_required"] == "1":
                    if not valid_visa(person["visa"]):
                        return_list.append("Reject")
                        continue
            elif person["entry_reason"].lower() == "transit":
                if json_countries[person["home"]["country"].upper()]["transit_visa_required"] == "1":
                    if not valid_visa(person["visa"]):
                        return_list.append("Reject")
                        continue
        except KeyError:
            return_list.append("Reject")
            continue

        try:
            found = 0
            for poi in json_watchlist:
                if (person["first_name"].upper() == poi["first_name"]) | \
                        (person["last_name"].upper() == poi["last_name"]):
                    found = 1
                    return_list.append("Secondary")
                    break
                elif person["passport"].upper() == poi["passport"]:
                    found = 1
                    return_list.append("Secondary")
                    break
            if found == 1:
                continue
        except KeyError:
            return_list.append("Reject")
            continue

        try:
            person["home"]["city"]
            person["home"]["region"]
            person["home"]["country"]
            person["from"]["city"]
            person["from"]["region"]
        except KeyError:
            return_list.append("Reject")
            continue

        return_list.append("Accept")

    return return_list


def valid_passport_format(passport_number):
    """
    Checks whether a passport number is five sets of five alpha-number characters separated by dashes
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


def valid_visa(visa):
    """
    Checks whether the visa is valid (its code is two groups of five
    alphanumeric characters separated by a dash, and it's less than 2 years old)
    :param visa: the visa to be checked
    :return: Boolean True if the visa is valid, False otherwise
    """
    try:
        if re.compile('.{5}-.{5}').match(visa["code"]):
            visa_date = datetime.datetime.strptime(visa["date"], '%Y-%m-%d')
            if visa_date + datetime.datetime(2, 0, 0) > datetime.datetime.today():
                return True
        return False
    except (KeyError, ValueError):
        return False


