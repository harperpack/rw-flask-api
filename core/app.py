from flask import Flask, request, jsonify
from flask_cors import cross_origin

import os
import json
import datetime
from traceback import print_exc

app = Flask(__name__)

FILE_PREFIX = 'files'
FILE_SUFFIX = '.json'
VERBOSE = True

## TODO
# > Add API keys / authentication
# > 
# > Ensure always wrapped in try/except (presumably cause of CORS outage?)
# > Strip file extensions?
# > Add /status endpoint?
# > Clean up file post disaster
# > 



def get_content(file_path, clear=False):
    try:
        if VERBOSE:
            print("Getting {}".format(file_path))
        if not os.path.exists(file_path): 
            return jsonify({"content":"Read Error | File path does not exist."}), 404
        with open(file_path, 'r', encoding='utf-8') as f:
            contents = json.load(f)
        if clear:
            set_contents(file_path, [], allow_blank=True)
        # if since:
        #     for index, content in enumerate(contents.get("content", [])):
        #         if content["time"] < since:
        #             del contents["content"][index:]
        #             break
        return jsonify(contents), 200
    except Exception as e:
        if VERBOSE:
            print("GET ERROR: {}: {}".format(e.__class__.__name__, e))
            print_exc()
        return jsonify({"content":"Read Error | {}: {}".format(e.__class__.__name__, e)}), 500

def set_contents(file_path, contents, allow_blank=False):
    # ASSUME CONTENTS ARE A LIST OF JSON OBJECTS
    try:
        if not allow_blank and not contents:
            return jsonify({"content": "Write Error | No write content specified."}), 400
        elif not allow_blank and not contents[0]:
            return jsonify({"content": "Write Error | No write content specified."}), 400
        json_to_write = {"content": contents}
        with open(file_path, 'w', encoding='utf-8') as f:
            if VERBOSE:
                print("Setting {} to {}".format(json_to_write, file_path))
            json.dump(json_to_write, f, ensure_ascii=False, indent=4)
        if allow_blank:
            return jsonify({"content":"Clear Success | Cleared {}".format(file_path)}), 201
        return jsonify({"content":"Write Success | Wrote to {}".format(file_path)}), 201
    except Exception as e:
        if VERBOSE:
            print("SET ERROR:{}: {}".format(e.__class__.__name__, e))
            print_exc()
        return jsonify({"content":"Write Error | {}: {}".format(e.__class__.__name__, e)}), 500

def get_path(file):
    return os.path.join(FILE_PREFIX, file+FILE_SUFFIX)

# def get_time(new_content):
    # ENFORCE ASSUMPTION THAT ALL CONTENT ARE JSON OBJECTS
    # what is that object?
    # if not isinstance(new_content, dict):
    #     print("HERE IS THE TYPE OF NEW_OBJ: {}".format(type(new_content)))
    #     new_content = {"content": new_content}
    # new_content["time"] = datetime.datetime.now().isoformat()
    # return new_content
    

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
                "in": "JSON object with key 'file' whose value is a string (the name of the file to be read).",
                "out": "JSON object with key 'content' whose value is a list of JSON content objects written to that specified file, or a String containing an error message.",
            },
            "/api/write/":{
                "doc": "Write the specified content to a specified file.",
                "in": "JSON object with key 'file', whose value is a sting (the name of the file to be written), and key 'content', whose value is the JSON object to be written to that file.",
                "out": "JSON object with key 'content' whose value is a String indicating the write operation was a success, or a String containing an error message.",
            },
        },
    },
    "header_parameters":{
        "file": "File to be read from or written to, without extension. API uses parameter to write to: files/{$file}.json",
        "content": "JSON object to be written to the specified file. File at files/<$file>.json will subsequently look like: {'content': {'time':<$timestamp>,<$other key-value pairs of JSON object found at key 'content' of header>},}",
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
    # if not input.get("time", ""):
    #     input["time"] = "2023-03-02T17:46:40.832589"
    if VERBOSE:
        # print("Reading latest content of {} since {}".format(input["file"], input["time"]))
        print("Reading the oldest piece of content in {} and then removing it.".format(input["file"]))
    # return get_content(get_path(input["file"]), since=input["time"])
    write_path = get_path(input["file"])
    response = get_content(write_path)
    read_content = response[0].json
    write_content = read_content.get('content', [])
    if not write_content:
        return jsonify({"content": []}), 200
    return_content = write_content.pop(0)
    set_contents(write_path, write_content, allow_blank=True)
    return jsonify({"content": return_content}), 200
    # return get_content(get_path(input["file"]), clear=True)

@app.route('/api/clear/', methods=['POST'])
@cross_origin()
def clear_content():
    input = request.json
    write_path = get_path(input["file"])
    if VERBOSE:
        print("Clearing content of {}".format(input["file"]))
    return set_contents(write_path, [], allow_blank=True)

@app.route('/api/write/', methods=['POST'])
@cross_origin()
def write_content():
    input = request.json
    # ASSUME ALL WRITE CONTENT IS A JSON OBJECT
    new_content = input.get('content', {})
    # new_content = get_time(new_content)
    # ASSUME CONTENT IS ALWAYS A LIST OF JSON OBJECTS
    write_content = [new_content]
    write_path = get_path(input["file"])
    if VERBOSE:
        print("Writing {} to {}.".format(write_content, input["file"]))
    return set_contents(write_path, write_content)

@app.route('/api/append/', methods=['POST'])
@cross_origin()
def append_content():
    try:
        input = request.json
        # ASSUME ALL APPEND CONTENT IS A JSON OBJECT
        # if something is already there, take and add time stamp, and append
        # 
        new_content = input.get('content', {})
        # new_content = get_time(new_content)
        write_path = get_path(input["file"])
        response = get_content(write_path)
        if response[1] == 200:
            read_content = response[0].json
            write_content = read_content.get('content', [])
            # IS WRITE_CONTENT NOW A LIST? MUST NOT BE
            while not isinstance(write_content, list):
                write_content = write_content.get("content", [])
            # ASSUME CONTENT IS ALWAYS A LIST OF JSON OBJECTS
            # write_content.insert(0, new_content)
            write_content.append(new_content)
        elif response[1] == 404:
            write_content = [new_content]
        else:
            # get_content() SHOULD ONLY RETURN 200 OR 404
            raise ValueError(f'{response[0].json}')
        if VERBOSE:
            print("Writing {} to {}.".format(write_content, input["file"]))
        return set_contents(write_path, write_content)
    except Exception as e:
        if VERBOSE:
            print("APPEND ERROR: {}: {}".format(e.__class__.__name__, e))
            print_exc()
        return jsonify({"content":"APPEND Error | {}: {}".format(e.__class__.__name__, e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0')