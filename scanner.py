#!/usr/bin/env python

tmpdir = '/var/local/share/tmp'
destdir = '/var/local/share'
logfile = '%s/scanlog.txt' % destdir

import argparse
import subprocess
from datetime import datetime

import logging
logging.basicConfig(filename=logfile, level=logging.INFO)


def config(folder, tmp_folder, log):
    global logfile
    global tmpdir
    global destdir
    logfile = log
    tmpdir = tmp_folder
    destdir = folder

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

        cmd = ['gm']
        cmd.append('convert')
        cmd.extend(['-compress', 'jpeg'])
        cmd.extend(['-quality', '80'])
        cmd.append('%s-scanned.tiff' % tmpfilename_prefix)
        cmd.append(destfilename)
        logging.info('Executing: %s' % subprocess.list2cmdline(cmd))
        try:
	    subprocess.check_call(cmd)
        except subprocess.CalledProcessError, e:
            logging.error('gm convert: %s' % e.output)
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

	cmd = ['gm']
	cmd.append('convert')
	cmd.extend(['-bordercolor','#9BA7AB'])
	cmd.extend(['-border', '1x1'])
	cmd.extend(['-fuzz', '18%'])
	cmd.append('-trim')
	cmd.append('+adjoin')
	cmd.append('%s-scanned-*.tiff' % tmpfilename_prefix)
	cmd.append('%s-trimmed-%%02d.tiff' % tmpfilename_prefix)
	logging.info('Executing: %s' % subprocess.list2cmdline(cmd))
        try:
	    subprocess.check_call(cmd)
        except subprocess.CalledProcessError, e:
            logging.error('gm convert: %s' % e.output)
            return ''

	cmd = ['gm']
	cmd.append('convert')
	cmd.append('+dither')
	cmd.extend(['-colors', '4'])
	cmd.extend(['-blur', '1'])
	cmd.extend(['-level', '10%,1,70%'])
	cmd.append('%s-trimmed-*.tiff' % tmpfilename_prefix)
	cmd.append(destfilename)
	logging.info('Executing: %s' % subprocess.list2cmdline(cmd))
        try:
	    subprocess.check_call(cmd)
        except subprocess.CalledProcessError, e:
            logging.error('gm convert: %s' % e.output)
            return ''

	return destfilename

    else:
        print 'not supported'

    return ''


