#!/usr/bin/python
#
#
#

import datetime
import html
import json
import os
import platform
import re
import sysconfig
import sys
from quart import Quart, request
from markupsafe import escape

app = Quart(__name__)

def add_if_exists(obj, key, value):
    if value:
        obj[key] = value

def handle_jsonp(data):
    str_data = json.dumps(data)
    callback = request.args.get("callback")
    if not callback:
        return str_data, 200, { "Content-Type": "application/json" }

    return f"{callback}({str_data})", 200, { "Content-Type": "application/javascript" }

@app.route("/")
async def root():
    return f"Running Python {platform.python_version()}", 200, { "Content-Type": "text/plain; charset=utf8;" }

@app.route("/status.json")
async def status_json():
    retVal = {}
    retVal["success"] = True
    retVal["message"] = "OK"
    retVal["commit"] = os.environ["COMMIT"] if "COMMIT" in os.environ else "local"
    retVal["timestamp"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    retVal["lastmod"] = os.environ["LASTMOD"] if "LASTMOD" in os.environ else "local"
    retVal["tech"] = "Python %d.%d.%d" % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    retVal["version"] = "%s" % (platform.python_version())
    add_if_exists(retVal, "platform.machine()", platform.machine())
    add_if_exists(retVal, "platform.node()", platform.node())
    #IOError: add_if_exists(retVal, "platform.platform()", platform.platform())
    add_if_exists(retVal, "platform.processor()", platform.processor())
    add_if_exists(retVal, "platform.python_branch()", platform.python_branch())
    add_if_exists(retVal, "platform.python_build()", platform.python_build())
    add_if_exists(retVal, "platform.python_compiler()", platform.python_compiler())
    add_if_exists(retVal, "platform.python_implementation()", platform.python_implementation())
    add_if_exists(retVal, "platform.python_version()", platform.python_version())
    add_if_exists(retVal, "platform.python_revision()", platform.python_revision())
    add_if_exists(retVal, "platform.release()", platform.release())
    add_if_exists(retVal, "platform.system()", platform.system())
    add_if_exists(retVal, "platform.version()", platform.version())
    add_if_exists(retVal, "platform.uname()", platform.uname())
    add_if_exists(retVal, "sysconfig.get_platform()", sysconfig.get_platform())
    add_if_exists(retVal, "sysconfig.get_python_version()", sysconfig.get_python_version())
    add_if_exists(retVal, "sys.byteorder", sys.byteorder)
    add_if_exists(retVal, "sys.getdefaultencoding()", sys.getdefaultencoding())
    add_if_exists(retVal, "sys.getfilesystemencoding()", sys.getfilesystemencoding())
    add_if_exists(retVal, "sys.maxsize", sys.maxsize)
    add_if_exists(retVal, "sys.maxunicode", sys.maxunicode)
    add_if_exists(retVal, "sys.version", sys.version)

    return handle_jsonp(retVal)

@app.route('/test.json', methods=['GET', 'POST'])
async def test_json():

    if request.method == 'POST':
        if request.content_type == 'application/json':
            rawJson = await request.get_json()
            testInput = {
                "regex": rawJson.get('regex', ''),
                "replacement": rawJson.get('replacement', ''),
                "inputs": rawJson.get('inputs', []),
                "options": rawJson.get('options', []),
            }
        else:
            form_data = await request.form
            testInput = {
                "regex": form_data.get('regex', ''),
                "replacement": form_data.get('replacement', ''),
                "inputs": form_data.getlist('input'),
                "options": form_data.getlist('option'),
            }
    else:
        testInput = {
            "regex": request.args.get('regex', ''),
            "replacement": request.args.get('replacement', ''),
            "inputs": request.args.getlist('input'),
            "options": request.args.getlist('option'),
        }

    sys.stderr.write("testInput: %s\n" % (testInput))

    regex = testInput['regex']
    if len(regex) == 0:
        return handle_jsonp({
            "success": False,
            "message": "No regex specified",
        })

    replacement = testInput['replacement']
    inputs = testInput['inputs']

    options = set(testInput['options'])
    flags = 0
    flagList = []
    if "ignorecase" in options:
        flags |= re.IGNORECASE
        flagList.append("IGNORECASE")
    if "locale" in options:
        flags |= re.LOCALE
        flagList.append("LOCALE")
    if "multiline" in options:
        flags |= re.MULTILINE
        flagList.append("MULTILINE")
    if "dotall" in options:
        flags |= re.DOTALL
        flagList.append("DOTALL")
    if "unicode" in options:
        flags |= re.UNICODE
        flagList.append("UNICODE")
    if "verbose" in options:
        flags |= re.VERBOSE
        flagList.append("VERBOSE")


    html_output = []
    html_output.append('<table class="table table-bordered table-striped" style="width:auto;">\n')
    html_output.append('\t<tbody>\n')

    html_output.append('\t\t<tr>\n')
    html_output.append('\t\t\t<td>')
    html_output.append('Regular Expression')
    html_output.append('</td>\n')
    html_output.append('\t\t\t<td>')
    html_output.append(html.escape(regex))
    html_output.append('</td>\n')
    html_output.append('\t\t</tr>\n')

    html_output.append('\t\t<tr>\n')
    html_output.append('\t\t\t<td>')
    html_output.append('as a raw Python string')
    html_output.append('</td>\n')
    html_output.append('\t\t\t<td>')
    html_output.append(html.escape("r'" + regex + "'"))
    html_output.append('</td>\n')
    html_output.append('\t\t</tr>\n')

    html_output.append('\t\t<tr>\n')
    html_output.append('\t\t\t<td>')
    html_output.append('as a regular Python string (with re.escape())')
    html_output.append('</td>\n')
    html_output.append('\t\t\t<td>')
    html_output.append(html.escape("'" + re.escape(regex)) + "'")
    html_output.append('</td>\n')
    html_output.append('\t\t</tr>\n')

    html_output.append('\t\t<tr>\n')
    html_output.append('\t\t\t<td>')
    html_output.append('replacement')
    html_output.append('</td>\n')
    html_output.append('\t\t\t<td>')
    html_output.append(html.escape(replacement))
    html_output.append('</td>\n')
    html_output.append('\t\t</tr>\n')

    if len(options) > 0:
        html_output.append('\t\t<tr>\n')
        html_output.append('\t\t\t<td>')
        html_output.append('flags (as constants)')
        html_output.append('</td>\n')
        html_output.append('\t\t\t<td>')
        html_output.append(html.escape("|".join(flagList)))
        html_output.append('</td>\n')
        html_output.append('\t\t</tr>\n')

    try:
        pattern = re.compile(regex, flags)
    except Exception as e:
        html_output.append('\t\t<tr>\n')
        html_output.append('\t\t\t<td>')
        html_output.append('Exception')
        html_output.append('</td>\n')
        html_output.append('\t\t\t<td>')
        html_output.append(html.escape(str(e)))
        html_output.append('</td>\n')
        html_output.append('\t\t</tr>\n')
        html_output.append('\t</tbody>\n')
        html_output.append('</table>\n')
        return json.dumps({"success": False, "message": "re.compile() Exception:" + str(e), "html": "".join(html_output)})

    if len(options) > 0:
        html_output.append('\t\t<tr>\n')
        html_output.append('\t\t\t<td>')
        html_output.append('flags')
        html_output.append('</td>\n')
        html_output.append('\t\t\t<td>')
        html_output.append(str(pattern.flags))
        html_output.append('</td>\n')
        html_output.append('\t\t</tr>\n')

    html_output.append('\t\t<tr>\n')
    html_output.append('\t\t\t<td>')
    html_output.append('# of groups (.group)')
    html_output.append('</td>\n')
    html_output.append('\t\t\t<td>')
    html_output.append(str(pattern.groups))
    html_output.append('</td>\n')
    html_output.append('\t\t</tr>\n')

    html_output.append('\t\t<tr>\n')
    html_output.append('\t\t\t<td>')
    html_output.append('Group name mapping (.groupindex)')
    html_output.append('</td>\n')
    html_output.append('\t\t\t<td>')
    html_output.append(str(pattern.groupindex))
    html_output.append('</td>\n')
    html_output.append('\t\t</tr>\n')

    html_output.append('\t</tbody>\n')
    html_output.append('</table>\n')

    html_output.append('<table class="table table-bordered table-striped">\n')
    html_output.append('\t<thead>\n')
    html_output.append('\t\t<tr>\n')
    html_output.append('\t\t\t<th style="text-align:center;">Test</th>\n')
    html_output.append('\t\t\t<th>Target String</th>\n')
    html_output.append('\t\t\t<th>findall()</th>\n')
    #html_output.append('\t\t\t<th>match()</th>\n')
    html_output.append('\t\t\t<th>split()</th>\n')
    html_output.append('\t\t\t<th>sub()</th>\n')
    html_output.append('\t\t\t<th>search()</th>\n')
    for loop in range(0, pattern.groups+1):
        html_output.append('\t\t\t<th>group(')
        html_output.append(str(loop))
        html_output.append(')</th>\n');

    html_output.append('\t\t</tr>');
    html_output.append('\t</thead>');
    html_output.append('\t<tbody>');

    for loop in range(0, len(inputs)):

        test = inputs[loop]

        if len(test) == 0:
            continue

        matcher = pattern.search(test)

        html_output.append('\t\t<tr>\n')
        html_output.append('\t\t\t<td style="text-align:center">')
        html_output.append(str(loop+1))
        html_output.append('</td>\n')

        html_output.append('\t\t\t<td>')
        html_output.append(html.escape(test))
        html_output.append('</td>\n')

        html_output.append('\t\t\t<td>')
        html_output.append(html.escape(str(pattern.findall(test))))
        html_output.append('</td>\n')

        #html_output.append('\t\t\t<td>')
        #html_output.append(html.escape(str(pattern.match(test))))
        #html_output.append('</td>\n')

        html_output.append('\t\t\t<td>')
        html_output.append(html.escape(str(pattern.split(test))))
        html_output.append('</td>\n')

        html_output.append('\t\t\t<td>')
        html_output.append(html.escape(str(pattern.sub(replacement, test))))
        html_output.append('</td>\n')

        html_output.append('\t\t\t<td>')
        if matcher:
            html_output.append("pos=%d&nbsp;start()=%d&nbsp;end()=%d" % (matcher.pos, matcher.start(), matcher.end()))
        html_output.append('</td>\n')

        for group in range(0, pattern.groups+1):
            html_output.append('\t\t\t<td>')
            if matcher:
                html_output.append(html.escape(matcher.group(group)))
            html_output.append('</td>\n');

        html_output.append('\t\t</tr>\n')

        while matcher:
            matcher = pattern.search(test, matcher.end())
            if matcher:
                html_output.append('\t\t<tr>\n');
                html_output.append('\t\t\t<td colspan="5">&nbsp;</td>\n')
                html_output.append('\t\t\t<td>')
                html_output.append("pos=%d&nbsp;start()=%d&nbsp;end()=%d" % (matcher.pos, matcher.start(), matcher.end()))
                html_output.append('</td>\n')

                for group in range(0, pattern.groups+1):
                    html_output.append('\t\t\t<td>')
                    html_output.append(html.escape(matcher.group(group)))
                    html_output.append('</td>\n');

                html_output.append('\t\t</tr>\n')


    html_output.append('\t</tbody>\n')
    html_output.append('</table>\n')



    return handle_jsonp({
        "success": True,
        "message": "OK",
        "html": "".join(html_output),
    })

if __name__ == "__main__":
    hostname = os.environ.get("HOSTNAME", "0.0.0.0")
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host=hostname, port=port)