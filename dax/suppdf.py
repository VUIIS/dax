import tempfile
import os
import glob
import socket
import yaml
import logging

from fpdf import FPDF
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger

from .XnatUtils import get_assessor_inputs
from .utilities import read_yaml
from .assessor_utils import parse_full_assessor_name, is_sgp_assessor
from .version import VERSION as dax_version

# TODO: recode this so the arguments are just the text to use
# for the header and footer parts, and we figure
# out the text outside of this function

# TODO: allow option to load description from the singularity README file.
# should this be the default if there's not one explicitly in the yaml?
# What would be the default location? This could default to use the
# "main container" if it is set.

LOGGER = logging.getLogger('dax')


def make_overpdf(overfile, info, pagenum, pagecount):
    # Assessor name top left of header
    # processor name and version left of footer
    # Date and Page numbers in right footer

    # Initialize the pdf
    pdf = FPDF(orientation="P", unit='in', format='letter')
    pdf.set_margins(left=0, top=0, right=0)
    pdf.add_page()
    pdf.set_font('courier', size=9)

    # Draw lines in header and footer
    pdf.set_draw_color(r=155, g=155, b=155)
    pdf.set_line_width(0.01)
    pdf.line(x1=0.2, y1=0.2, x2=8.3, y2=0.2)
    pdf.line(x1=0.2, y1=10.7, x2=8.3, y2=10.7)

    # Write the assessor label in the header
    pdf.set_xy(0.3, 0.1)
    pdf.cell(0, 0.05, '{}'.format(info['assessor']))

    # Prevent footer from falling off page
    pdf.set_auto_page_break(False)

    # Write proc version in left of footer
    pdf.set_xy(0.3, -0.2)
    pdf.cell(0, 0, '{}'.format(info['proctype']))

    # Write date in right of footer
    pdf.set_xy(-2.1, -0.2)
    pdf.cell(0, 0, '{}'.format(info['procdate']))

    # Write page numbers right of footer
    pdf.set_xy(-0.6, -0.2)
    pdf.cell(0, 0, '{}/{}'.format(pagenum, pagecount))

    # Write the pdf to file
    pdf.output(overfile)


def make_lastpdf(lastfile, info):
    pdf = FPDF(orientation="P", unit='in', format='letter')
    pdf.add_page()

    LOGGER.debug('making last page for PDF')

    # Session Info
    pdf.ln(0.05)
    for key, val in info['session'].items():
        pdf.set_font('helvetica', size=13)
        pdf.cell(w=1.1, h=.4, txt=key, border=0)
        pdf.set_font('courier', size=14)
        pdf.cell(w=6.7, h=.4, txt=val, border=1, ln=1)

    # Inputs
    pdf.ln(0.5)
    pdf.set_font('helvetica', size=14)
    pdf.cell(1, .2, 'INPUTS:', ln=2)

    # Inputs - data rows
    for r in info['inputs']:
        pdf.set_font('courier', size=12)
        pdf.cell(w=1.25, h=.3, txt=r[0], border=0)
        pdf.cell(w=1, h=.3, txt=r[1][-6:], border=1, align='C')
        pdf.set_font('courier', size=7)
        pdf.cell(w=6, h=.3, txt=(r[2].split('/assessors/')[-1])[-90:], border=0, ln=1)

    # Outputs
    pdf.ln(0.5)
    pdf.set_font('helvetica', size=14)
    pdf.cell(1, .2, 'OUTPUTS:', ln=2)

    # Outputs - header row
    pdf.set_font('helvetica', style='B', size=12)
    pdf.cell(w=1.5, h=.3, txt='resource', border=1)
    pdf.cell(w=0.6, h=.3, txt='type', border=1, align='C')
    pdf.cell(w=5.6, h=.3, txt='path', border=1, ln=1)

    # Outputs - data rows
    pdf.set_font('courier', size=12)
    for out in info['outputs']:
        pdf.cell(w=1.5, h=.3, txt=out['resource'], border=1)
        pdf.cell(w=0.6, h=.3, txt=out['type'], border=1, align='C')
        pdf.cell(w=5.6, h=.3, txt=out['path'], border=1, ln=1)

    # Job Info
    pdf.ln(0.5)
    joby = pdf.get_y()
    pdf.set_font('helvetica', size=14)
    pdf.cell(1, .2, 'JOB:', ln=2)
    pdf.set_font('courier', size=12)

    for k, v in info['job'].items():
        # Show label
        pdf.set_font('helvetica', size=12)
        pdf.cell(w=0.8, h=.3, txt=k, border=0)

        # Show value
        pdf.set_font('courier', size=12)
        pdf.cell(w=1, h=.3, txt=v, border=1, ln=1)

    # Proc Info
    pdf.ln(0.5)
    pdf.set_y(joby)
    pdf.set_font('helvetica', size=14)
    pdf.set_x(2.5)
    pdf.cell(1, .2, '', ln=1)
    for k, v in info['proc'].items():
        pdf.set_x(2.5)
        pdf.set_font('helvetica', size=12)
        pdf.cell(w=1.2, h=.3, txt=k, border=0)
        pdf.set_font('courier', size=12)
        pdf.cell(w=4.4, h=.3, txt=v, border=1, ln=1)

    # Show Description
    pdf.set_font('helvetica', size=14)
    pdf.ln(0.5)
    pdf.cell(0, .1, 'DESCRIPTION:', ln=2)
    pdf.ln(0.01)
    pdf.set_font('courier', size=10)
    pdf.multi_cell(0, .2, txt=info['description'])

    # Save to file
    LOGGER.debug('saving last page of PDF to file:{}'.format(lastfile))
    try:
        pdf.output(lastfile)
    except Exception as err:
        LOGGER.error('saving PDF:{}:{}'.format(lastfile, err))


def make_suppdf(outfile, info, infile=None, overlay=True):
    # Make the overlay PDF
    tempdir = tempfile.mkdtemp()
    lastfile = os.path.join(tempdir, 'last.pdf')
    mergedfile = os.path.join(tempdir, 'merged.pdf')

    # Make last pages of pdf
    try:
        make_lastpdf(lastfile, info)
    except Exception as err:
        import traceback
        traceback.print_stack()
        LOGGER.error('error making PDF:{}:{}'.format(lastfile, err))

    # Append last page(s)
    merger = PdfFileMerger()

    # Start with the input pdf if we have one
    if infile:
        merger.append(PdfFileReader(infile))

    # Append out last page(s)
    merger.append(PdfFileReader(lastfile))

    # Write the merged PDF file
    merger.write(mergedfile)

    # Load the merged PDF
    newpdf = PdfFileReader(open(mergedfile, "rb"))
    pagecount = newpdf.getNumPages()

    # Initialize the new pdf
    output = PdfFileWriter()

    # Iterate pages in existing PDF to add overlays
    for i in range(newpdf.getNumPages()):
        pagenum = i + 1
        overfile = os.path.join(tempdir, '{}.pdf'.format(pagenum))
        try:
            make_overpdf(overfile, info, pagenum, pagecount)
        except Exception as err:
            ('error making PDF', err)

        # Load the overlay PDF we just made
        overpdf = PdfFileReader(overfile)

        # Merge the two
        page = newpdf.getPage(i)
        page.mergePage(overpdf.getPage(0))

        # Append merged page to output
        output.addPage(page)

    # Write to file
    with open(outfile, "wb") as f:
        output.write(f)


def get_this_instance():
    # build the instance name
    this_host = socket.gethostname().split('.')[0]
    this_user = os.environ['USER']
    return '{}@{}'.format(this_user, this_host)


def load_version(assr_path):
    with open(os.path.join(assr_path, 'version.txt'), 'r') as f:
        return f.read().strip()


def load_attr(assr_path, attr):
    filepath = os.path.join(
            os.path.dirname(assr_path),
            'DISKQ',
            attr,
            os.path.basename(assr_path))

    with open(filepath, 'r') as f:
        return f.readline().strip()


def load_description(assr_path):
    processor_path = load_attr(assr_path, 'processor')
    with open(processor_path, "r") as yaml_stream:
        doc = yaml.load(yaml_stream, Loader=yaml.FullLoader)

    return doc.get('description', '')


def load_procyamlversion(assr_path):
    processor_path = load_attr(assr_path, 'processor')
    LOGGER.debug('loading procyamlversion from file:{}'.format(processor_path))
    with open(processor_path, "r") as yaml_stream:
        doc = yaml.load(yaml_stream, Loader=yaml.FullLoader)

    return doc.get('procyamlversion', '')


def load_inputs(assr_obj):
    assr_inputs = get_assessor_inputs(assr_obj)
    inputs = []

    for k, v in assr_inputs.items():
        inputs.append((k, v.split('/')[-1], v))

    return inputs


def load_outputs(assr_path):
    outputs = []
    processor_path = load_attr(assr_path, 'processor')

    doc = read_yaml(processor_path)

    for c in doc.get('outputs', []):
        LOGGER.debug('suppdf:load_outputs:{}'.format(c))
        # Check for keywords
        if 'pdf' in c:
            _path = c['pdf']
            _type = 'FILE'
            _res = 'PDF'
        elif 'dir' in c:
            _path = c['dir']
            _type = 'DIR'
            _res = c['dir']
        elif 'stats' in c:
            _path = c['stats']
            _type = 'FILE'
            _res = 'STATS'

        # Get explicitly set path, type, resource
        # These will override anything set by keywords
        if 'path' in c:
            _path = c['path']

        if 'type' in c:
            _type = c['type']

        if 'resource' in c:
            _res = c['resource']

        # Add to our outputs list
        outputs.append({
            'path': _path,
            'type': _type,
            'resource': _res})

    return outputs


def load_info(assr_path, assr_obj):
    info = {}

    # Load info
    assr = parse_full_assessor_name(os.path.basename(assr_path))

    LOGGER.debug('loading info:{}'.format(assr))

    info['assessor'] = assr['label']

    # Load
    LOGGER.debug('loading version')
    info['procdate'] = load_attr(assr_path, 'jobstartdate')

    # Load job info
    LOGGER.debug('loading job info')
    info['job'] = {
        'jobid': load_attr(assr_path, 'jobid'),
        'duration': load_attr(assr_path, 'walltimeused'),
        'memory': load_attr(assr_path, 'memused')}

    # Load proc info
    LOGGER.debug('loading proc info')
    info['proc'] = {
        'dax_version': str(dax_version),
        'dax_manager': get_this_instance()}

    # Load procyaml version
    LOGGER.debug('suppdf:load_info:load_procyamlversion')
    info['procyamlversion'] = load_procyamlversion(assr_path)

    # Load the description from the processor yaml
    LOGGER.debug('suppdf:load_info:load_description')
    info['description'] = load_description(assr_path)

    # Load inputs from XNAT assessor/inputs
    LOGGER.debug('suppdf:load_info:load_inputs')
    info['inputs'] = load_inputs(assr_obj)

    # Load outputs from the processor yaml
    LOGGER.debug('suppdf:load_info:load_outputs')
    info['outputs'] = load_outputs(assr_path)

    if is_sgp_assessor(os.path.basename(assr_path)):
        info['proctype'] = info['assessor'].split('-x-')[2]
        info['session'] = {
            'PROJECT': assr['project_id'],
            'SUBJECT': assr['subject_label']}
    else:
        info['proctype'] = info['assessor'].split('-x-')[3]
        info['session'] = {
            'PROJECT': assr['project_id'],
            'SUBJECT': assr['subject_label'],
            'SESSION': assr['session_label']}

    LOGGER.debug('suppdf:load_info:finished')
    return info


def suppdf(assr_path, assr_obj):
    try:
        info = load_info(assr_path, assr_obj)
        if info['procyamlversion'] != '3.0.0-dev.0':
            LOGGER.debug('skipping suppdf:{}, procyamlversion={}'.format(
                assr_path, info['procyamlversion']))
            return False
    except Exception as err:
        LOGGER.debug('skipping suppdf:{}:err={}'.format(assr_path, err))
        return False

    LOGGER.debug('suppdf:={}'.format(info))

    # find the input pdf
    try:
        inputpdf = glob.glob(assr_path + '/PDF/*.pdf')[0]
    except Exception:
        inputpdf = None

    # Make sure the output dir exists
    try:
        os.mkdir(os.path.join(assr_path, 'PDF'))
    except FileExistsError:
        pass

    # Name the output with assessor name
    outputpdf = '{}/PDF/report_{}.pdf'.format(assr_path, info['assessor'])

    if inputpdf == outputpdf:
        LOGGER.debug('PDF already supped:{}'.format(inputpdf))
        return

    # supplement it by adding header/footer overlays
    make_suppdf(outputpdf, info, inputpdf, overlay=True)

    # delete the input pdf
    if inputpdf and os.path.exists(outputpdf):
        LOGGER.debug('deleting input PDF:{}'.format(inputpdf))
        os.remove(inputpdf)
