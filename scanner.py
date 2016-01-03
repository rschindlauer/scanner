#!/usr/bin/env python

tmpdir = '/var/local/share/tmp'
destdir = '/var/local/share'
logfile = '%s/scanlog.txt' % destdir

import argparse
import subprocess
from datetime import datetime

import logging

def config(folder, tmp_folder, log):
    global logfile
    global tmpdir
    global destdir
    logfile = log
    tmpdir = tmp_folder
    destdir = folder
    logging.basicConfig(filename=logfile, level=logging.INFO)

def process_photo(infile, outfile):
    cmd = ['gm']
    cmd.append('convert')
    cmd.extend(['-compress', 'jpeg'])
    cmd.extend(['-quality', '80'])
    cmd.append(infile)
    cmd.append(outfile)
    logging.info('Executing: %s' % subprocess.list2cmdline(cmd))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError, e:
        logging.error('gm convert: %s' % e.output)
        return ''

    return destfilename

def is_blank_page(file):
    cmd = ['gm']
    cmd.append('identify')
    cmd.append('-verbose')
    cmd.append(file)
    result = subprocess.check_output(cmd)

    blank = True

    import re
    mStdDev = re.compile("""\s*Standard Deviation:\s*\d+\.\d+\s*\((?P<percent>\d+\.\d+)\).*""")
    for line in result.splitlines():
        match = mStdDev.search(line)
        if match:
            stdev = float(match.group('percent'))
            #print stdev
            if stdev > 0.1:
                return False
                break
    return True

def create_pdf(inpattern, outfile, remove_blanks=True):
    import glob
    import os

    process_cmd = ['gm']
    process_cmd.append('convert')
    process_cmd.extend(['-bordercolor','#9BA7AB'])
    process_cmd.extend(['-border', '1x1'])
    process_cmd.extend(['-fuzz', '18%'])
    process_cmd.append('-trim')
	# process_cmd.append('+adjoin')

    listing = glob.glob(inpattern)
    for filename in listing:
        if not is_blank_page(filename):
            cmd = list(process_cmd)
            cmd.append(filename)
            without_extension = os.path.splitext(filename)[0]
            cmd.append('%s-trimmed.tiff' % without_extension)
            logging.info('Executing: %s' % subprocess.list2cmdline(cmd))
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError, e:
                logging.error('gm convert: %s' % e.output)
                return ''
        else:
            logging.info('%s is a blank page, skipping' % filename)

    pattern_without_extension = os.path.splitext(inpattern)[0]
    processed_pattern = '%s-trimmed.tiff' % pattern_without_extension

    cmd = ['gm']
    cmd.append('convert')
    cmd.append('+dither')
    cmd.extend(['-colors', '4'])
    cmd.extend(['-blur', '1'])
    cmd.extend(['-level', '10%,1,70%'])
    cmd.append(processed_pattern)
    cmd.append(outfile)
    logging.info('Executing: %s' % subprocess.list2cmdline(cmd))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError, e:
        logging.error('gm convert: %s' % e.output)
        return ''

    return True

def scan(mode):
    global logfile
    global tmpdir
    global destdir

    timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

    tmpfilename_prefix = '%s/%s' % (tmpdir, timestamp)
    destfileprefix = '%s/%s' % (destdir, timestamp)

    logging.info('Scan attempt at %s ================' % timestamp)

    if mode == 'photo':

        destfilename = '%s.jpg' % destfileprefix

        cmd = ['scanimage']
        cmd.append('-B')
        cmd.extend(['--mode', 'Color'])
        cmd.extend(['--page-height', '0'])
        cmd.extend(['--brightness', '30'])
        cmd.extend(['--format', 'tiff'])
        logging.info('Executing: %s' % subprocess.list2cmdline(cmd))
        f = open('%s-scanned.tiff' % tmpfilename_prefix, 'w')
        try:
            subprocess.check_call(cmd, stdout=f)
        except subprocess.CalledProcessError, e:
            logging.error('scanimage: %s' % e.output)
            return ''

        if not process_photo(infile='%s-scanned.tiff' % tmpfilename_prefix,
                             outfile=destfilename):
            return ''

        return destfilename

    elif mode in ['front', 'duplex']:

        destfilename = '%s.pdf' % destfileprefix

        scan_source =  'ADF Front' if mode == 'front' else 'ADF Duplex'

        cmd = ['scanimage']
        cmd.append('-B')
        cmd.extend(['--mode', 'Color'])
        cmd.extend(['--page-height', '0'])
        cmd.extend(['--format', 'tiff'])
        cmd.append('--batch=%s-scanned-%%02d.tiff' % tmpfilename_prefix)
        cmd.extend(['--source', scan_source])
        logging.info('Executing: %s' % subprocess.list2cmdline(cmd))
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError, e:
            # only 7 is ok, means feeder out of documents at the end of a scan
            if e.returncode != 7:
                logging.error('scanimage: %s' % e.output)
                return ''

        if not create_pdf(inpattern='%s-scanned-*.tiff' % tmpfilename_prefix,
                          outfile=destfilename):
            return ''

        return destfilename

    else:
        print 'not supported'

    return ''
