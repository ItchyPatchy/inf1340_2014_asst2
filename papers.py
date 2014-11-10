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
    # loads each input file through file reader, and defines as json file.

    for person in json_input:
        try:
            if person["from"]["country"].upper() != "KAN":
                if json_countries[person["from"]["country"].upper()]["medical_advisory"] != "":
                    return_list.append("Quarantine")
                    continue
                    # checks if country of origin (not Kanadia) has medical advisory. Returns Quarantine if true

        except KeyError:
            return_list.append("Reject")
            continue
            # return reject on incomplete or incorrect information in this input section

        try:
            if json_countries[person["via"]["country"].upper()]["medical_advisory"] != "":
                return_list.append("Quarantine")
                continue
                # checks if person has travelled through country with medical advisory. Returns Quarantine if true.
        except KeyError:
            pass
            # does nothing since "via" is not a required field

        try:
            if not (valid_passport_format(person["passport"]) & valid_date_format(person["birth_date"])):
                return_list.append("Reject")
                continue
                # checks if passport and birth date adhere to the correct format, as defined by a separate function
        except KeyError:
            return_list.append("Reject")
            continue
            # return reject on incomplete or incorrect information in this input section
            # (same reasoning in expression in following except block)

        try:
            if person["entry_reason"].lower() == "visit":
                if json_countries[person["home"]["country"].upper()]["visitor_visa_required"] == "1":
                    if not valid_visa(person["visa"]):
                        return_list.append("Reject")
                        continue
                        # if entry reason and home country both require a visa, then rejects if input visa is invalid
            elif person["entry_reason"].lower() == "transit":
                if json_countries[person["home"]["country"].upper()]["transit_visa_required"] == "1":
                    if not valid_visa(person["visa"]):
                        return_list.append("Reject")
                        continue
                        # if entry reason is transit and a transit visa is needed, then rejects if input visa is invalid
        except KeyError:
            return_list.append("Reject")
            continue

        # check if fields in "home" and "from" are lacking
        try:
            person["home"]["city"]
            person["home"]["region"]
            person["home"]["country"]
            person["from"]["city"]
            person["from"]["region"]
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
                    # compares first and last name of input to person of interest list for match.  Secondary if true
                elif person["passport"].upper() == poi["passport"]:
                    found = 1
                    return_list.append("Secondary")
                    break
                    # compares passport number of input to person of interest list.
            if found == 1:
                continue
        except KeyError:
            return_list.append("Reject")
            continue

        return_list.append("Accept")
        # returns accept if all other conditions pass

    return return_list


def valid_passport_format(passport_number):
    """
    Checks whether a passport number is five sets of five alpha-number characters separated by dashes
    :param passport_number: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('^\w{5}-\w{5}-\w{5}-\w{5}-\w{5}$')

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
        if re.compile('^\w{5}-\w{5}$').match(visa["code"]):
            visa_date = datetime.datetime.strptime(visa["date"], '%Y-%m-%d')
            if visa_date + datetime.timedelta(days=365 * 2) > datetime.datetime.today():
                return True
        return False
    except (KeyError, ValueError):
        return False
