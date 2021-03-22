#!/usr/bin/python
# coding=UTF-8
#
# Auto EQ Server
#
# Copyright © 2021 Carl Wilson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Code for the headphone data model."""
import os
import re
from zipfile import ZipFile
from urllib.parse import unquote

from flask import current_app

from autoeq_srv.routes.const import (
    MNFCT_FILE,
    OVER_EAR, IN_EAR,
    PHONE_TYPE_DETAILS,
    README,
    REC_RESULTS,
    RES_ROOT,
    SOURCES
)

APP = current_app

def _get_phone_type(to_parse):
    return IN_EAR if IN_EAR in to_parse else OVER_EAR

def _result_instance(source, name, target, model):
    return {
        'source': source,
        'name': name,
        'type': PHONE_TYPE_DETAILS[_get_phone_type(target)],
        'target' : target,
        'model' : model
    }

def _manufacturers_with_variants():
    """Return the raw manufacturers data including variants."""
    with open(MNFCT_FILE,
              encoding='utf-8') as _fh:
        raw_manufacturers = _fh.read().strip().split('\n')
        manufacturers = [m.strip().split('\t') for m in raw_manufacturers]
    return manufacturers

RAW_MANUFACTURERS = _manufacturers_with_variants()

def get_manufacturers():
    """Return the manufacturers list."""
    manufacturers = []
    for manufacturer in RAW_MANUFACTURERS:
        manufacturers.append(manufacturer[0])
    return manufacturers

MANUFACTURERS = get_manufacturers()

def resolve_manufacturer(name):
    """Return a canonical name and variant tuple."""
    for manufacturer in RAW_MANUFACTURERS:
        if name in manufacturer:
            return manufacturer[0], name
    return None

def get_results_map():
    """Return all results."""
    results = {}
    for source in SOURCES:
        results[source] = parse_results_file(source,
                                             os.path.join(RES_ROOT, source, README))
    return results

def parse_results_file(source, results_file):
    """Return the list of recommended headphone results parsed from the README.md"""
    results = []
    # Open the results file
    with open(results_file, 'r',
              encoding='utf-8') as _fh:
        # Split it on the newlines
        raw_recs = _fh.read().strip().split('\n')
        # For each line
        for raw_rec in raw_recs:
            # Regex to get the name, target and model path
            tup_srch = re.search(r'- \[(.*)\]\(.\/(.*)\/(.*)\)', raw_rec)
            # If we get a match
            if tup_srch:
                results.append(_result_instance(source,
                                                tup_srch.group(1),
                                                tup_srch.group(2),
                                                tup_srch.group(3)))
    return results

RESULTS = get_results_map()

def get_results(source):
    """Return all of the results for the supplied source."""
    return RESULTS[source]

def get_recommended_results():
    """Return the list of recommended headphone results parsed from the README.md"""
    recommendations = []
    with open(REC_RESULTS, 'r',
              encoding='utf-8') as _fh:
        raw_recs = _fh.read().strip().split('\n')
        for raw_rec in raw_recs:
            tup_srch = re.search(r'- \[(.*)\]\(.\/(.*)\/(.*)\/(.*)\)', raw_rec)
            if tup_srch:
                recommendations.append(_result_instance(tup_srch.group(2),
                                                        tup_srch.group(1),
                                                        tup_srch.group(3),
                                                        tup_srch.group(4)))
    return recommendations

RECOMMENDED = get_recommended_results()

def get_phone_results(to_scan, phone_type):
    """Return a list of phone directories."""
    phones = []
    for phone_dir in [ name for name in os.listdir(to_scan) \
                       if os.path.isdir(os.path.join(to_scan, name)) ]:
        phones.append({
                'name': phone_dir,
                'type': PHONE_TYPE_DETAILS[phone_type]
                })
    return phones

def get_filters(source, target, model):
    """Return the zipped convolution filters for the specified measurement source,
    target and headphone model."""
    phone_model = unquote(model)
    phone_path = os.path.join(RES_ROOT,
                              source,
                              target,
                              phone_model)
    if not os.path.isdir(phone_path):
        return None
    zip_name = '{}_{}_results.zip'.format(phone_model, target)
    zip_path = os.path.join(phone_path, zip_name)
    if not os.path.isfile(zip_path):
        with ZipFile(zip_path, 'w') as reszip:
            filter_name =  '{} minimum phase 44100Hz.wav'.format(phone_model)
            reszip.write(os.path.join(phone_path, filter_name), arcname=filter_name)
            filter_name =  '{} minimum phase 48000Hz.wav'.format(phone_model)
            reszip.write(os.path.join(phone_path, filter_name), arcname=filter_name)
    return phone_path, zip_name
