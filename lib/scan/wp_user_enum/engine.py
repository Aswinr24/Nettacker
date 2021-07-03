#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Pradeep Jairamani , github.com/pradeepjairamani

import socket
import socks
import time
import json
import threading
import string
import random
import sys
import re
import os
from core.alert import warn, info, messages
from core.targets import target_type
from core.targets import target_to_host
from core.load_modules import load_file_path
from lib.socks_resolver.engine import getaddrinfo
from core._time import now
from core.log import __log_into_file
import requests
from core.decor import main_function, socks_proxy


def extra_requirements_dict():
    return {"wp_user_enum_ports": [80, 443]}




def wp_user_enum(
    target,
    port,
    timeout_sec,
    log_in_file,
    language,
    time_sleep,
    thread_tmp_filename,
    socks_proxy,
    scan_id,
    scan_cmd,
):
    try:
        
        from core.conn import connection
        s = connection(target, port, timeout_sec, socks_proxy)

        if not s:
            return False
        else:
            if target_type(target) != "HTTP" and port == 443:
                target = "https://" + target
            if target_type(target) != "HTTP" and port == 80:
                target = "http://" + target
            user_agent_list = [
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; \
                    rv:1.8.0.5) Gecko/20060719 Firefox/1.5.0.5",
                "Googlebot/2.1 ( http://www.googlebot.com/bot.html)",
                "Mozilla/5.0 (X11; U; Linux x86_64; en-US) \
                    AppleWebKit/534.13 (KHTML, like Gecko) Ubuntu/10.04"
                " Chromium/9.0.595.0 Chrome/9.0.595.0 Safari/534.13",
                "Mozilla/5.0 (compatible; MSIE 7.0; Windows NT 5.2;\
                     WOW64; .NET CLR 2.0.50727)",
                "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22\
                     Version/10.51",
                "Debian APT-HTTP/1.3 (0.8.10.3)",
                "Mozilla/5.0 (compatible; Googlebot/2.1;\
                     +http://www.google.com/bot.html)",
                "Googlebot/2.1 (+http://www.googlebot.com/bot.html)",
                "Mozilla/5.0 (compatible; Yahoo! Slurp;\
                     http://help.yahoo.com/help/us/ysearch/slurp)",
                "YahooSeeker/1.2 (compatible; Mozilla 4.0; MSIE 5.5;\
                     yahooseeker at yahoo-inc dot com ; "
                "http://help.yahoo.com/help/us/shop/merchant/)",
            ]
            headers = {"User-agent": random.choice(user_agent_list)}
            r = requests.get(
                target + "/?feed=rss2", verify=False, headers=headers
            )
            r2 = requests.get(
                target + "/?author=", verify=False, headers=headers
            )
            r3 = requests.get(
                target + "/wp-json/wp/v2/users", verify=False, headers=headers
            )
            try:
                r3List = json.loads(r3.text)
            except Exception:
                r3List = []
            wp_users_admin3 = []
            try:
                global wp_users
                wp_users_feed = re.findall(
                    r"<dc:creator><!\[CDATA\[(.+?)\]\]></dc:creator>",
                    r.text,
                    re.IGNORECASE,
                )
                wp_users_admin = re.findall(
                    "author author-(.+?) ", r2.text, re.IGNORECASE
                )
                wp_users_admin2 = re.findall(
                    "/author/(.+?)/feed/", r2.text, re.IGNORECASE
                )
                for i in r3List:
                    wp_users_admin3.append(i["slug"])
                wp_users = (
                    wp_users_feed
                    + wp_users_admin
                    + wp_users_admin2
                    + wp_users_admin3
                )
                wp_users = sorted(set(wp_users))
                if wp_users != "":
                    return True
                else:
                    return False
            except Exception:
                return False
    except Exception:
        return False


def __wp_user_enum(
    target,
    port,
    timeout_sec,
    log_in_file,
    language,
    time_sleep,
    thread_tmp_filename,
    socks_proxy,
    scan_id,
    scan_cmd,
):
    if wp_user_enum(
        target,
        port,
        timeout_sec,
        log_in_file,
        language,
        time_sleep,
        thread_tmp_filename,
        socks_proxy,
        scan_id,
        scan_cmd,
    ):
        info(
            messages(language, "found").format(
                target, "Wordpress users found ", ", ".join(wp_users)
            )
        )
        __log_into_file(thread_tmp_filename, "w", "0", language)
        for i in wp_users:
            data = json.dumps(
                {
                    "HOST": target,
                    "USERNAME": i,
                    "PASSWORD": "",
                    "PORT": port,
                    "TYPE": "wp_user_enum_scan",
                    "DESCRIPTION": messages(language, "found").format(
                        target, "Wordpress user found ", i
                    ),
                    "TIME": now(),
                    "CATEGORY": "vuln",
                    "SCAN_ID": scan_id,
                    "SCAN_CMD": scan_cmd,
                }
            )
            __log_into_file(log_in_file, "a", data, language)
        return True
    else:
        return False

@main_function(extra_requirements_dict(), __wp_user_enum, "wp_user_enum_scan", "wp_user_enum_scan")
def start(
    target,
    users,
    passwds,
    ports,
    timeout_sec,
    thread_number,
    num,
    total,
    log_in_file,
    time_sleep,
    language,
    verbose_level,
    socks_proxy,
    retries,
    methods_args,
    scan_id,
    scan_cmd,
):  # Main function
    pass