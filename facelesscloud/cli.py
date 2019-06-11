#! /usr/bin/python3
# -*- coding: utf-8 -*-

""" CLI functions """

import sys
import json
import aaargh
import urllib3
import requests
import pyqrcode
import simplejson
from sshpubkeys import SSHKey


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Yes I know it's ugly. Please feel free to change it :)

FC_URL = 'https://api.facelesscloud.com/api/'
CLI_APP = aaargh.App()


class Bcolors:
    """ Color Class """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[32m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def convert_to_qrcode(str_to_convert):
    """ Convert any string to qrcode. Return qr.terminal string. """
    qrcode = pyqrcode.create(str_to_convert)
    return qrcode.terminal(module_color='black', background='white', quiet_zone=1)


def file_to_string(file_path):
    """ Simple function that read a file. Return a string. """
    data = ''
    try:
        with open(file_path, 'r') as file:
            data = file.read()
        file.close()
    except FileNotFoundError as err:  # Sublime give an error, but it's not.
        print(Bcolors.FAIL + 'ERROR: ' + file_path + ' not found.' + Bcolors.ENDC)
        print(str(err))
        sys.exit(2)
    except PermissionError as err:
        print(Bcolors.FAIL + 'ERROR: ' + file_path + ', Permission Denied.' + Bcolors.ENDC)
        print(str(err))
        sys.exit(2)
    return data


def validate_ssh_key(ssh_key):
    """ Validates an ssh_key argument. """
    result = None
    if ssh_key is None:
        result = True  # If None we don't care
    if not isinstance(ssh_key, str):
        result = False
    ssh_key_object = SSHKey(ssh_key, skip_option_parsing=True, disallow_options=True)
    try:
        ssh_key_object.parse()
        result = True
    except Exception:
        result = False
    return result


def api_get(func, data=None):
    """ Doing a simple http get call. Return JSON. """
    result = {}
    try:
        req = requests.get(FC_URL + func, params=data, verify=False)
        result.update({'status': req.status_code, 'result': req.json()})
    except requests.exceptions.RequestException as error:
        result.update({'status': 'ERROR', 'result': str(error)})
    except simplejson.errors.JSONDecodeError as error:
        print(str(req))
        print(str(error))
    return result


def api_post(func, data=None):
    """ Doing a simple http post call, data must be a dict. Return JSON. """
    result = {}
    try:
        req = requests.post(FC_URL + func, data=json.dumps(data), verify=False)
        result = req.json()
        result.update({'status': req.status_code})
    except requests.exceptions.RequestException as error:
        result.update({'status': 'ERROR : ' + str(error)})
    except simplejson.errors.JSONDecodeError as error:
        print(str(req))
        print(str(error))
    return result


def get_region_id(region_name):
    """ Get region id from name. Return region id. """
    region_id = None
    all_region = api_get('region')
    if all_region.get('status') == 200:
        region_data = all_region.get('result')
        for region in region_data:
            if region_data[region].get('name') == region_name:
                region_id = region_data[region].get('DCID')
    return region_id


@CLI_APP.cmd(help='Return all available Region.')
def get_region():
    all_region = api_get('region')
    if all_region.get('status') == 200:
        print(json.dumps(all_region.get('result'), indent=4, sort_keys=True))
    else:
        print(Bcolors.FAIL + str(all_region) + Bcolors.ENDC)


@CLI_APP.cmd(help='Return all available Operating System.')
def get_os():
    operating_system = api_get('os')
    if operating_system.get('status') == 200:
        print(json.dumps(operating_system.get('result'), indent=4, sort_keys=True))
    else:
        print(Bcolors.FAIL + str(operating_system) + Bcolors.ENDC)


@CLI_APP.cmd(help='Return all available Flavor.')
def get_flavor():
    all_flavor = api_get('flavor')
    if all_flavor.get('status') == 200:
        print(json.dumps(all_flavor.get('result'), indent=4, sort_keys=True))
    else:
        print(Bcolors.FAIL + str(all_flavor) + Bcolors.ENDC)


@CLI_APP.cmd(help='Step by step make config file helper.')
def makeconf():
    """ Conf helper, making a .JSON file with configuration. Return nothing. """
    conf = {}
    available_locations = []
    print('Hi. We will help you make a config file.')
    input('Press ENTER to continue or CTRL+C to quit.... ')
    path = input('Please enter the path you want to save the config file. Default . (4nt direcoty) : ')
    time = input('How long, in hours, you would like the instance to leave? Default 24 (hours) : ')
    flavor = input('What is the Instance Flavor ID you would like to spawn? Default 201 (CPU:1, MEM:1gb, SSD:25gb) : ')
    operating_system = input('What is the Instance operating system ID you would like to install? Default 167 (CentOS 7) : ')
    currency = input('Which currency would you like to pay with? "bitcoin, ethereum, litecoin or bitcoincash". Default (bitcoin)')
    all_flavor = api_get('flavor')
    all_os = api_get('os')

    path = path if path else './instance-conf.json'
    time = time if time else '24'
    flavor = flavor if flavor else '201'
    operating_system = operating_system if operating_system else '167'
    currency = currency if currency else 'bitcoin'

    if not all_flavor.get('status') == 200 or not all_os.get('status') == 200:
        print(Bcolors.FAIL + 'ERROR: Something went wrong requesting facelesscloud server.' + Bcolors.ENDC)
        sys.exit(2)

    if not all_flavor['result'].get(flavor):
        print(Bcolors.FAIL + 'ERROR: flavor ID entered does not exist.' + Bcolors.ENDC)
        sys.exit(2)
    if not all_os['result'].get(operating_system):
        print(Bcolors.FAIL + 'ERROR: operating system ID entered does not exist.' + Bcolors.ENDC)
        sys.exit(2)

    available_locations = all_flavor['result'][flavor].get('available_locations')
    if not available_locations:
        print(Bcolors.FAIL + 'ERROR: No available location found for specified flavor.' + Bcolors.ENDC)
        sys.exit(2)

    i = 1
    location_num = {}
    for location in available_locations:
        location_num.update({i: location})
        i = i + 1

    region = input('Please select region to deploy instance ' + str(location_num) + ' : ')

    if int(region) not in location_num:
        print(Bcolors.FAIL + 'ERROR: Region ID selected not in displayed choice. Exiting no configuration file created.' + Bcolors.ENDC)
        sys.exit(2)

    region_id = get_region_id(location_num.get(int(region)))

    sshkey_path = input('Please enter the Public SSH Key path. (Let it blank if None.) : ')
    sshkey = file_to_string(sshkey_path) if sshkey_path else None
    kickstart_path = input('Please enter the kickstart Bash script path. (Let it blank if None.) : ')
    kickstart = file_to_string(kickstart_path) if kickstart_path else None

    if sshkey and not validate_ssh_key(sshkey):
        print(Bcolors.FAIL + 'ERROR: SSH-KEY format is bad ! Exiting no configuration file created.' + Bcolors.ENDC)
        sys.exit(2)

    conf.update({'hours_time': time, 'flavor': flavor, 'operating_system': operating_system, 'region': region_id, 'ssh_key': sshkey, 'kickstart': kickstart, 'currency': currency})
    try:
        with open(path, 'w') as conf_file:
            json.dump(conf, conf_file)
        conf_file.close()
    except FileNotFoundError as err:  # Sublime give an error, but it's not.
        print(Bcolors.FAIL + 'ERROR: Config File path entered not found.' + Bcolors.ENDC)
        print(str(err))
        sys.exit(2)
    except PermissionError as err:
        print(Bcolors.FAIL + 'ERROR: Config File path entered, Permission Denied.' + Bcolors.ENDC)
        print(str(err))
        sys.exit(2)

    print(Bcolors.OKGREEN + 'SUCCESS, Config file writen to ' + path + Bcolors.ENDC)


@CLI_APP.cmd(help='Instance Spawing function.')
@CLI_APP.cmd_arg('-c', '--configfile', type=str, default=None, help='Path of the config File. You can generate one with the subcommand "makeconf".')
@CLI_APP.cmd_arg('-t', '--time', type=str, default='24', help='Instance life time in hours. Default 24')
@CLI_APP.cmd_arg('-m', '--currency', type=str, default='bitcoin', help='Curreny that you want to use. "bitcoin, ethereum, litecoin or bitcoincash" Default bitcoin.')
@CLI_APP.cmd_arg('-f', '--flavor', type=str, default='201', help='Instance Flavor ID. Default (201). CPU:1, MEM:1gb, SSD:25gb')
@CLI_APP.cmd_arg('-o', '--operating_system', type=str, default='167', help='Operating System ID. Default (167) CentOS 7.')
@CLI_APP.cmd_arg('-r', '--region', type=str, default='1', help='Region location ID. Default (1) New Jersey.')
@CLI_APP.cmd_arg('-s', '--sshkey', type=str, default=None, help='Public SSH Key file path.')
@CLI_APP.cmd_arg('-k', '--kickstart', type=str, default=None, help='kickstart Bash Script path to execute at the instance startup.')
@CLI_APP.cmd_arg('-x', '--force', type=bool, default=False, help='Ignore parameters checker if True and force sending spawn data.')
def spawn(
        configfile,
        time,
        flavor,
        operating_system,
        region,
        currency,
        sshkey,
        kickstart,
        force):
    """ Create new instance. Return Transaction info as print. """
    if configfile:
        try:
            with open(configfile, 'r') as file:
                data = file.read()
            file.close()
            data = json.loads(data)
        except FileNotFoundError as err:  # Sublime give an error, but it's not.
            print(Bcolors.FAIL + 'ERROR: Config File path entered not found.' + Bcolors.ENDC)
            print(str(err))
            sys.exit(2)
        except PermissionError as err:
            print(Bcolors.FAIL + 'ERROR: Config File path entered, Permission Denied.' + Bcolors.ENDC)
            print(str(err))
            sys.exit(2)
    else:
        sshkey = file_to_string(sshkey) if sshkey else None
        kickstart = file_to_string(kickstart) if kickstart else None
        data = {
            'hours_time': time,
            'flavor': flavor,
            'operating_system': operating_system,
            'region': region,
            'ssh_key': sshkey,
            'kickstart': kickstart,
            'currency': currency
        }

    validation = False

    if not force:
        while not validation:
            print(json.dumps(data, indent=4, sort_keys=True))
            val_question = input('Is theses parameter are correct ? [Y / N] : ')
            if val_question in ['Y', 'y']:
                validation = True
            elif val_question in ['N', 'n']:
                print(Bcolors.FAIL + 'Instance creation/spawning stoped.' + Bcolors.ENDC)
                sys.exit(2)

    api_returned_info = api_post('create', data)

    if api_returned_info and api_returned_info.get('status') == 200:
        instance_info = api_returned_info.get('Request_instance')
        status = instance_info.get('Status')
        transaction = instance_info.get('Transaction')
        color = Bcolors.OKGREEN if status == 'SUCCESS' else Bcolors.FAIL

        print('New Instance requested... ' + color + status + Bcolors.ENDC)
        for message in instance_info.get('Message'):
            print(Bcolors.OKBLUE + message + Bcolors.ENDC)

        if transaction and status == 'SUCCESS':
            print(' ')
            print('---------- QR CODE ----------')
            print(convert_to_qrcode(transaction.get('Address')))
            print(Bcolors.WARNING + json.dumps(transaction, indent=4, sort_keys=True) + Bcolors.ENDC)
            print(' ')
            print('You can now look at the transaction and instance status, using the subcommand "status" with above "Transaction_ID".')
            print('E.G. : "facelesscloud status -i 13c3febe-ac0a-448f-9404-005b4475063e" (transaction_id)')
            print(' ')
            return True  # For assert test.
        else:
            print(Bcolors.FAIL + 'ERROR : ' + Bcolors.ENDC + 'Something went wrong calling the server.')
            print(json.dumps(api_returned_info, indent=4, sort_keys=True))
            sys.exit(2)
    else:
        print(Bcolors.FAIL + 'ERROR : ' + Bcolors.ENDC + 'Something went wrong calling the server.')
        print(json.dumps(api_returned_info, indent=4, sort_keys=True))
        sys.exit(2)


@CLI_APP.cmd(help='Get Instance/Transaction Status. Returning instance info (IP, Password, etc), if ready')
@CLI_APP.cmd_arg('-i', '--transaction_id', type=str, help='Transaction ID returned by spawn function.')
def status(transaction_id):
    """ Returning Transaction Status and Instance informations. """
    instance_status = api_get('status', {'transaction_id': transaction_id})
    if instance_status.get('status') == 200:
        print(json.dumps(instance_status, indent=4, sort_keys=True))
    else:
        print(Bcolors.FAIL + str(instance_status) + Bcolors.ENDC)


@CLI_APP.cmd(help='Instance extend function.')
@CLI_APP.cmd_arg('-s', '--subid', type=str, help='ID of the running instance. SUBID.')
@CLI_APP.cmd_arg('-t', '--extendtime', type=str, help='Time in hours that you would like to extend')
@CLI_APP.cmd_arg('-m', '--currency', type=str, default='bitcoin', help='Curreny that you want to use. "bitcoin, ethereum, litecoin or bitcoincash" Default bitcoin.')
def extend(subid, extendtime, currency):
    """ Instance subscription extend. """
    if not subid or not extendtime:
        print(Bcolors.FAIL + 'Missing parameters --subid  or  --extendtime . Extend aborded...' + Bcolors.ENDC)
        sys.exit(2)
    data = {'subid': subid, 'expend_time': extendtime, 'currency': currency}
    api_returned_info = api_post('extend', data)
    print(api_returned_info)

    if api_returned_info and api_returned_info.get('status') == 200:
        instance_info = api_returned_info.get('Request_extend')
        status = instance_info.get('Status')
        transaction = instance_info.get('Transaction')
        color = Bcolors.OKGREEN if status == 'SUCCESS' else Bcolors.FAIL

        print('Instance Time extend requested... ' + color + status + Bcolors.ENDC)
        for message in instance_info.get('Message'):
            print(Bcolors.OKBLUE + message + Bcolors.ENDC)

        if transaction and status == 'SUCCESS':
            print(' ')
            print('---------- QR CODE ----------')
            print(convert_to_qrcode(transaction.get('Address')))
            print(Bcolors.WARNING + json.dumps(transaction, indent=4, sort_keys=True) + Bcolors.ENDC)
            print(' ')
            print('You can now look at the transaction and instance status, using the subcommand "status" with above "Transaction_ID".')
            print('E.G. : "facelesscloud status -i 13c3febe-ac0a-448f-9404-005b4475063e" (transaction_id)')
            print(' ')
            return True  # For assert test.
        else:
            print(Bcolors.FAIL + 'ERROR : ' + Bcolors.ENDC + 'Something went wrong calling the server.')
            print(json.dumps(api_returned_info, indent=4, sort_keys=True))
            sys.exit(2)
    else:
        print(Bcolors.FAIL + 'ERROR : ' + Bcolors.ENDC + 'Something went wrong calling the server.')
        print(json.dumps(api_returned_info, indent=4, sort_keys=True))
        sys.exit(2)


def main():
    """ Main function. Return CLI run. """
    CLI_APP.run()


if __name__ == '__main__':
    main()
