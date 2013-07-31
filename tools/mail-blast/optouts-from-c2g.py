#!/usr/bin/env python
#
# Assumes that on both C2G and EdX jumpbox machines you have a .my.cnf
# file that points to the datbase that you want to query.  Best if its
# a readonly replica, but not strictly required.  The .my.cnf file should
# look something like this.
#
#  [client]
#       user=username
#       database=dbname
#    password=password
#       host=endpointname.us-west-2.rds.amazonaws.com
#
# Also assumes that you have a ssh agent running that gives can get you
# to the jumpbox / deploy server
#

import sys
import os
import subprocess
import csv
import random
import math
import optparse
import re
import unicodedata

CHECK_EMAILS_TO_SEND = 10
JUMPBOX_USERNAME="sef"

def parsecommandline():
    usage = """usage: %prog [options]

Will create optout entries in edx from Class2Go optouts.  Info
messages to stderr.  Assumes that you can get to the edx readonly
database from your jumpbox, and the Class2Go readonly database from
the deploy server."""

    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-c", dest="check",
            help="addr to insert at beginning, end, through the mail list.  %d mails will be sent." % CHECK_EMAILS_TO_SEND)
    parser.add_option("-n", dest="checknum", action="store_false", default=True,
            help="don't insert chech numbers in email addresses")

    (options, args) = parser.parse_args()

    if options.check:
        m=re.match(r"([A-Z0-9._%+-]+)@([A-Z0-9.-]+\.[A-Z]{2,4})", options.check, re.I)
        if not m:
            parser.error("%s isn't a valid email address" % options.check)
        (name, domain) = m.group(1,2)
        if options.checknum:
            name += "+%03d"
        options.checkline = '"","%s@%s"' % (name, domain)
    if options.checknum == False and not options.check:
        parser.error("nonum option valid with check address option")

    return (options, args)
    

def remove_diacritic(input):
    """ 
    Accept a unicode string, and return a normal string without any
    diacritical marks.

    From: http://code.activestate.com/recipes/576648-remove-diatrical-marks-including-accents-from-stri/
    """ 
    return unicodedata.normalize('NFKD', unicode(input, 'ISO-8859-1')).encode('ASCII', 'ignore')


def dict_from_database(purpose, sql_query, proxy, command_template):
    """
    Returns a dictionary with email key and values list of course_ids enrolled
    """

    result = dict()

    print >> sys.stderr, "%s: SQL Query:" % purpose
    print >> sys.stderr, sql_query
    print >> sys.stderr

    cmd = command_template % (proxy, sql_query)
    cmd = cmd.replace('\n', ' ')

    print >> sys.stderr, "%s: Remote Command:" % purpose
    print >> sys.stderr, cmd
    print >> sys.stderr

    raw_list = subprocess.check_output(cmd, shell=True)

    warnings = 0
    errors = 0
    for line in raw_list.split(os.linesep):
        if line == "":
            continue
        try:
            (email, course_id) = line.split('\t')
            k = email.lower().encode('ascii')
        except Exception as e:
            print >>sys.stderr, "ERROR (%s): skip: %s" % (purpose, line)
            errors += 1
        else:
            if k in result:
                result[k].append(course_id)
            else:
                result[k] = [course_id]
    print >> sys.stderr, "edx query found=%d students, %d warnings, %d errors" % (len(result), warnings, errors)
    return result


def print_separator_to_stderr():
    print >> sys.stderr 
    print >> sys.stderr, "-------------------------------------------------------"
    print >> sys.stderr 


def print_checkline(options, lineno, checklines, force=False):
    if options.check and (lineno % options.checkfreq == 0 or force):
        if options.checknum:
            formatted_line = options.checkline % checklines
        else:
            formatted_line = options.checkline
        print formatted_line
        checklines += 1
    return checklines


def main():
    (options, args) = parsecommandline()

    # Query EdX for Students enrolled in any course
    sql_query_template="""select u.email, s.course_id
from student_courseenrollment s, auth_user u
where s.user_id = u.id"""
    sql_query = sql_query_template
    proxy = "%s@jump.prod.class.stanford.edu" % JUMPBOX_USERNAME
    command_template = """ssh %s "mysql -e \\"%s\\"" """
    students = dict_from_database("enrolled_students", sql_query, proxy, command_template)

    # Get Excludes list from Class2Go
    print_separator_to_stderr()
    sql_query = "select addr,'none' from c2g_emailaddr where optout=1"
    proxy = "%s@deploy.dev.c2gops.com" % JUMPBOX_USERNAME
    command_template = """ssh %s "mysql -e \\"%s\\"" """
    excludes = dict_from_database("excludes", sql_query, proxy, command_template)

    # Build insert statements for optouts
    optouts = 0
    insert_statements = ""
    for k,v in students.iteritems():
        if excludes.has_key(k):
            for course_id in v:
                insert_statements += "INSERT IGNORE INTO bulk_email_optout (email, course_id) VALUES ('%s', '%s');\n" % (k, course_id)
                print >> sys.stderr, "Added insert statement for optout for %s from %s" % (k, course_id)
                optouts += 1

    # proxy = "%s@jump.prod.class.stanford.edu" % JUMPBOX_USERNAME
    # command_template = """ssh %s "mysql -e \\"%s\\"" """
    # cmd = command_template % (proxy, insert_statements)
    # result = subprocess.check_output(cmd, shell=True) #raises CalledProcessError if error, success otherwise

    print insert_statements

    # Summary at the end to stderr
    print_separator_to_stderr()
    print >> sys.stderr, "INFO: found %d" % len(students)
    print >> sys.stderr, "INFO: %d new optout objects created from optout list of %d" % (optouts, len(excludes))

    
if __name__ == '__main__':
    main()
