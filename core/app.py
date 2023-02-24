from flask import Flask, request, jsonify
# from flask_cors import CORS
from flask_cors import cross_origin

import os
import json
import datetime
from traceback import print_exc

app = Flask(__name__)
# CORS(app)

FILE_PREFIX = 'files'
FILE_SUFFIX = 'file.json'
VERBOSE = False

def get_content(file_path, only_if_new=False):
    try:
        if VERBOSE:
            print("Getting {}".format(file_path))
        if not os.path.exists(file_path.replace(FILE_SUFFIX,"")):
            return jsonify({"content":"Read Error | File path does not exist."}), 404
        with open(file_path, 'r', encoding='utf-8') as f:
            contents = json.load(f)
        if only_if_new and not contents["new"]:
            return jsonify({"content":""}), 200
        contents["new"] = False
        print("Sending {} to be written to {}".format(contents["content"], file_path))
        set_contents(file_path, contents, new=False)
        return jsonify(contents), 200
        # return jsonify({"content":contents["content"]}), 200
    except Exception as e:
        if VERBOSE:
            print("GET ERROR: {}: {}".format(e.__class__.__name__, e))
            print_exc()
        return jsonify({"content":"Read Error | {}: {}".format(e.__class__.__name__, e)}), 500

def set_contents(file_path, contents, new=True):
    try:
        if not contents.get('content', ''):
            return jsonify({"content": "Write Error | No write content specified."}), 400
        if isinstance(contents['content'], str) and not contents.get('content', '').strip():
            return jsonify({"content": "Write Error | No write content specified."}), 400
        os.makedirs(get_path(contents["file"], dir_only=True), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            if new:
                contents["new"] = True
                contents["time"] = datetime.datetime.now().isoformat()
            if VERBOSE:
                print("Setting {} to {}".format(contents, file_path))
            json.dump(contents, f, ensure_ascii=False, indent=4)
        return jsonify({"content":"Write Success | Wrote to {}".format(contents["file"])}), 201
    except Exception as e:
        if VERBOSE:
            print("SET ERROR:{}: {}".format(e.__class__.__name__, e))
            print_exc()
        return jsonify({"content":"Write Error | {}: {}".format(e.__class__.__name__, e)}), 500

def get_path(file, dir_only=False):
    if dir_only:
        return os.path.join(FILE_PREFIX, file)
    return os.path.join(FILE_PREFIX, file, FILE_SUFFIX)

routes = {
    "endpoints":{
        "GET":{
            "/api/help/":{
                "doc": "List the API endpoints.",
                "in": "n/a",
                "out": "JSON object with methods, explanations, and i/o for each API endpoint."
            },
        },
        "POST":{
            "/api/read/":{
                "doc": "Read the content of a specified file.",
                "in": "JSON object with key 'file' whose value is the file to be read.",
                "out": "JSON object with key 'content' whose value is the text content of the specified file, or a String containing an error message.",
            },
            "/api/latest/":{
                "doc": "Get latest content of a specified file, if that file is unread.",
                "in": "JSON object with key 'file' whose value is the file to be read.",
                "out": "JSON object with key 'content' whose value is the text content of the specified file (if the file is unread, else this value is an empty String), or a String containing an error message.",
            },
            "/api/write/":{
                "doc": "Write the specified content to a specified file.",
                "in": "JSON object with key 'file', whose value is the file to be written, and key 'content', whose value is the text to be written to that file.",
                "out": "JSON object with key 'content' whose value is a String indicating the write operation was a success, or a String containing an error message.",
            },
            "/api/append/":{
                "doc": "Update the content to a specified file.",
                "in": "JSON object with key 'file', whose value is the file to be written, and key 'content', whose value is the text to be written to that file.",
                "out": "JSON object with key 'content' whose value is the text content of the specified file (if the file is unread), or an empty String (if the file is not unread).",
            },
        },
    },
    "header_parameters":{
        "file": "File to be read from or written to, without extension. API uses parameter to create directory: files/$file/file.json",
        "content": "JSON object to be written to the specified file.",
    },
}

@app.route('/')
@cross_origin()
def hello():
    return '<h1>Hello, World!</h1><br><h2>This does nothing.</h2>'

@app.route('/api/help/', methods=['GET'])
@cross_origin()
def list_content():
    if VERBOSE:
        print("Available endpoints.")
    return jsonify(routes)

@app.route('/api/read/', methods=['POST'])
@cross_origin()
def read_content():
    input = request.json
    if VERBOSE:
        print("Reading content of {}".format(input["file"]))
    return get_content(get_path(input["file"]))

@app.route('/api/latest/', methods=['POST'])
@cross_origin()
def latest_content():
    input = request.json
    if VERBOSE:
        print("Checking if file at {} has been read.".format(input["file"]))
    return get_content(get_path(input["file"]), only_if_new=True)

@app.route('/api/write/', methods=['POST'])
@cross_origin()
def write_content():
    input = request.json
    if VERBOSE:
        print("Writing {} to {}.".format(input["content"], input["file"]))
    return set_contents(get_path(input["file"]), input)

@app.route('/api/append/', methods=['POST'])
@cross_origin()
def append_content():
    try:
        input = request.json
        if VERBOSE:
            print("Appending {} to {}.".format(input["content"], input["file"]))
        file_path = get_path(input["file"])
        response = get_content(file_path)
        contents = {"content": '', "file": input["file"]}
        if response[1] == 200:
            contents = response[0].json
            if not (isinstance(contents["content"], type(input["content"])) or isinstance(input["content"], type(contents["content"]))):
                return jsonify({"content":"Append Error | Read type of {} ({}) different from write type ({}).".format(input["file"], type(contents["content"]), type(input["content"]))}), 400
            elif isinstance(contents.get("content", ""), str):
                contents["content"] = contents.get("content", "") + ' \n' + input.get("content", "")
            elif isinstance(contents.get("content", []), list):
                contents["content"].extend(input.get("content", []))
            elif isinstance(contents["content"], dict):
                try:
                    # todo test
                    for key in input.get("content", {}):
                        if key in contents["content"].keys():
                            key = key + "_0"
                            while key in contents["content"].keys():
                                key = key.rpartition('_')[0] + '_' + str(int(key.rpartition('_')[2])+1)
                        contents["content"][key] = input["content"][key]
                except Exception as e:
                    return jsonify({"content":"Append Error | {}: {}".format(e.__class__.__name__, e)}), 500
            else:
                return jsonify({"content":"Append Error | {} type not supported (only support str, list, and dict).".format(type(contents["content"]))}), 400
        elif response[1] == 404:
            contents["content"] = input.get("content", "")
        else:
            raise ValueError(f'{response[0].json}')
        return set_contents(file_path, contents)
    except Exception as e:
        if VERBOSE:
            print("APPEND ERROR: {}: {}".format(e.__class__.__name__, e))
            print_exc()
        return jsonify({"content":"Append Error | {}: {}".format(e.__class__.__name__, e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0')