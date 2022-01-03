import json
import uuid

import numpy as np
import requests.exceptions
from flask import Flask, request, Response, got_request_exception
from flask_restx import Resource, Api
import pandas as pd
from data import Data
import base64 as b64
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.debug = True
api = Api(app, prefix="/api/v1", version="1", title="User Management")
dataObj = Data()
dataDfUuid = dataObj.get_df_uuid()


@app.errorhandler(404)
def page_not_found(error):
    notFoundAllSites = \
        {
            "problem":
                {
                    "type": "https://httpstatuses.com/404",
                    "summary": "The requested URL was not found on the server.",
                    "status": 404,
                    "error_code": 1,
                    "details": "Site not found on the server. If you entered the URL manually please check your "
                               "spelling and try again.",
                    "information": request.base_url + "/error/1",
                }
        }
    return Response(json.dumps(notFoundAllSites), status=404)


"""@app.errorhandler(405)
def method_not_allowed(error):
    print(error)
    methodNotAllowedError = \
        {
            "problem":
                {
                    "type": "https://httpstatuses.com/404",
                    "summary": "The method is not allowed for the requested URL.",
                    "status": 405,
                    "error_code": 2,
                    "details": "Site not found on the server. If you entered the URL manually please check your "
                               "spelling and try again ",
                    "information": request.base_url + "/error/9",
                }
        }
    return Response(json.dumps(methodNotAllowedError), status=405)"""

"""code:
200 
201
400  POST 5, PUT 50, DELETE 7
404 GET(keine seite, alle seiten) 1, GET (User not found ) 2, POST(Fehler beim Ausführen) 3, PUT (User Not found) 4, DELETE (User Not found) 6 
405 GET 8
406 GET 9 GET 10, POST 11, PUT 12, DELETE 13
409 POST 14, PUT 15, 
415 Post 16
 """


@api.doc(responses={
    200: "OK",
    406: "Not Acceptable"
})
@api.route('/users')
class Users(Resource):
    def get(self):
        dataDfUuid = dataObj.get_df_uuid()
        query = ""
        if request.headers.get('accept') == "*/*" or request.headers.get('accept') == "application/json":
            if len(request.query_string.decode()) >= 1:
                query = request.query_string.decode()
                split = query.split(sep="=")
                if split[0] == "sort":
                    if "+" in split[1]:
                        asc = split[1].split(sep="+")
                        dataDfUuid = dataDfUuid.sort_values(by=[asc[1]], ascending=True)
                    elif "-" in split[1]:
                        dsc = split[1].split(sep="-")
                        dataDfUuid = dataDfUuid.sort_values(by=[dsc[1]], axis=0, ascending=False)

                    else:
                        dataDfUuid = dataDfUuid.sort_values(by=[split[1]], ascending=True)
                    response = Response(
                        dataDfUuid.drop(columns=["password"]).to_json(orient="records", default_handler=str),
                        mimetype='application/json',
                        status=200)
                    response.headers["location"] = "/api/v1/users?" + query
                    return response

                elif split[0] == "q":
                    search = split[1].split(sep=":")
                    if search[0] == "zipCode" or search[0] == "phoneNumber":
                        dataDfUuid = dataDfUuid.loc[dataDfUuid[search[0]] == int(search[1])]
                    else:
                        dataDfUuid = dataDfUuid.loc[dataDfUuid[search[0]] == search[1]]
                    response = Response(
                        dataDfUuid.drop(columns=["password"]).to_json(orient="records", default_handler=str),
                        mimetype='application/json',
                        status=200)
                    response.headers["location"] = "/api/v1/users?" + query
                    return response
            else:
                response = Response(
                    dataDfUuid.drop(columns=["password"]).to_json(orient="records", default_handler=str),
                    mimetype='application/json',
                    status=200)
                response.headers["location"] = "/api/v1/users"
                return response
        else:
            notAcceptableError = \
                {
                    "problem":
                        {
                            "type": "https://httpstatuses.com/406",
                            "summary": "Only application/json or */* is supported in the Accept header.",
                            "status": 406,
                            "error_code": 2,
                            "details": "The supplied Accept header is not supported.",
                            "information": "http://127.0.0.1:5000/api/v1/users" + query + "/error/2",
                        }
                }
            return Response(json.dumps(notAcceptableError), status=406)


@api.doc(responses={
    200: "OK",
    404: "Not Found",
    406: "Not Acceptable"
})
@api.route('/users/<string:uuid>')
class Users(Resource):
    def get(self, uuid):
        dataDfUuid = dataObj.get_df_uuid()
        if request.headers.get('accept') == "*/*" or request.headers.get('accept') == "application/json":
            incrUuid = 0
            compareUuid = dataDfUuid['uuid'].isin([uuid])
            for boolUuid in compareUuid:
                if boolUuid == False:
                    incrUuid = incrUuid + 1
                else:
                    replacedDfValue = dataDfUuid.drop(columns=["password"]).iloc[[incrUuid]].to_json(orient="records",
                                                                                                     default_handler=str).replace(
                        "[", "")
                    responseDfJson = replacedDfValue.replace("]", "")
                    response = Response(responseDfJson, mimetype='application/json', status=200)
                    response.headers["location"] = "/api/v1/users/" + str(uuid)
                    return response
            userNotFoundError = \
                {
                    "problem":
                        {
                            "type": "https://httpstatuses.com/404",
                            "summary": "No user could be found in the system with the given Universally Unique Identifier (UUID).",
                            "status": 404,
                            "error_code": 3,
                            "details": "User was not found.",
                            "information": "http://127.0.0.1:5000/api/v1/users/" + str(uuid) + "/error/3",
                        }
                }
            return Response(json.dumps(userNotFoundError), status=404)
        else:
            notAcceptableError = \
                {
                    "problem":
                        {
                            "type": "https://httpstatuses.com/406",
                            "summary": "Only application/json or */* is supported in the Accept header.",
                            "status": 406,
                            "error_code": 4,
                            "details": "The supplied Accept header is not supported.",
                            "information": "http://127.0.0.1:5000/api/v1/users/" + str(uuid) + "/error/4",
                            "uuid": str(uuid)
                        }
                }
            return Response(json.dumps(notAcceptableError), status=406)


@api.doc(responses={
    201: "Created",
    400: "Bad Request",
    406: "Not Acceptable",
    409: "Conflict",
    415: "Unsupported Media Type"
})
@api.route("/users")
class signUp(Resource):
    def post(self):
        try:
            newUuid = uuid.uuid4()
            if request.headers.get('accept') == "*/*" or request.headers.get('accept') == "application/json":
                if "application/json" in request.headers["Content-Type"]:
                    if request.get_json()["sex"] == "Mr" or request.get_json()["sex"] == "Ms" or request.get_json()[
                        "sex"] == "Mrs":
                        sex = request.get_json()["sex"]
                    if request.get_json()["firstName"] != "":
                        firstName = request.get_json()["firstName"]
                    if request.get_json()["lastName"] != "":
                        lastName = request.get_json()["lastName"]
                    if request.get_json()["address"] != "":
                        address = request.get_json()["address"]
                    if request.get_json()["city"] != "":
                        city = request.get_json()["city"]
                    if request.get_json()["zipCode"] != "":
                        zipCode = request.get_json()["zipCode"]
                    if request.get_json()["phoneNumber"] != "":
                        phoneNumber = request.get_json()["phoneNumber"]
                    if request.get_json()["email"] != "":
                        email = request.get_json()["email"]
                    if request.get_json()["password"] != "":
                        password = request.get_json()["password"]

                    dataDfUuid = dataObj.get_df_uuid()
                    incr = 0
                    compareEmail = dataDfUuid['email'].isin([email])
                    for bool in compareEmail:
                        if bool == False:
                            incr = incr + 1
                        else:
                            conflictError = \
                                {
                                    "problem":
                                        {
                                            "type": "https://httpstatuses.com/409",
                                            "summary": "The given e-mail is already used by another user.",
                                            "status": 409,
                                            "error_code": 5,
                                            "details": "E-mail is already used!",
                                            "information": "http://127.0.0.1:5000/api/v1/users" + "/error/5",
                                        }
                                }
                            return Response(json.dumps(conflictError), status=409)
                    if incr == int(len(compareEmail)):
                        dataDfUuid = dataObj.get_df_uuid().append({"sex": sex,
                                                                   "firstName": firstName,
                                                                   "lastName": lastName,
                                                                   "address": address,
                                                                   "city": city,
                                                                   "zipCode": zipCode,
                                                                   "phoneNumber": phoneNumber,
                                                                   "email": email,
                                                                   "password": password,
                                                                   "uuid": newUuid
                                                                   }, ignore_index=True)
                        newUserDf = pd.DataFrame({"sex": sex,
                                                  "firstName": firstName,
                                                  "lastName": lastName,
                                                  "address": address,
                                                  "city": city,
                                                  "zipCode": zipCode,
                                                  "phoneNumber": phoneNumber,
                                                  "email": email,
                                                  "uuid": newUuid
                                                  }, index=[0])
                        replacedDfValue = newUserDf.to_json(orient="records", default_handler=str).replace("[", "")
                        responseDfJson = replacedDfValue.replace("]", "")
                        dataObj.set_df_uuid(dataDfUuid)
                        response = Response(responseDfJson, mimetype='application/json',
                                            status=201)
                        response.headers["location"] = "/api/v1/users"
                        return response
                else:
                    unsupportetMediaTypeError = \
                        {
                            "problem":
                                {
                                    "type": "https://httpstatuses.com/415",
                                    "summary": "The supplied Content-Type header is not supported."
                                               "Only application/json is supported as Content-Type.",
                                    "status": 415,
                                    "error_code": 6,
                                    "details": "The message has not been sent in json. The Api supports only json.",
                                    "information": "http://127.0.0.1:5000/api/v1/users" + "/error/6",
                                }
                        }
                    return Response(json.dumps(unsupportetMediaTypeError), status=415)

            else:
                notAcceptableError = \
                    {
                        "problem":
                            {
                                "type": "https://httpstatuses.com/406",
                                "summary": "Only application/json or */* is supported in the Accept header.",
                                "status": 406,
                                "error_code": 7,
                                "details": "The supplied Accept header is not supported.",
                                "information": "http://127.0.0.1:5000/api/v1/users" + "/error/7",
                            }
                    }
                return Response(json.dumps(notAcceptableError), status=406)
        except Exception as e:
            splittedE = str(e).split(": ", 1)[1]
            eStatus = str(e).split()
            catchAllErrors = \
                {
                    "problem":
                        {
                            "type": "https://httpstatuses.com/" + eStatus[0],
                            "summary": splittedE,
                            "status": int(eStatus[0]),
                            "error_code": 8,
                            "details": "Error was triggered while processing the request.",
                            "information": "http://127.0.0.1:5000/api/v1/users" + "/error/8",
                        }
                }
            return Response(json.dumps(catchAllErrors), status=int(eStatus[0]))


@api.doc(responses={
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    406: "Not Acceptable",
    409: "Conflict"
})
@api.route('/users/<string:uuid>')
class updateUser(Resource):
    def put(self, uuid):
        try:
            if request.headers.get('accept') == "*/*" or request.headers.get('accept') == "application/json":
                if request.headers.get("Authorization") == None:
                    unauthorizedError = \
                        {
                            "problem":
                                {
                                    "type": "https://httpstatuses.com/401",
                                    "summary": "There was no Authorization data send. The Data in Authorization Header is None",
                                    "status": 401,
                                    "error_code": 9,
                                    "details": "No Authorization data was send with the request",
                                    "information": "http://127.0.0.1:5000/api/v1/users/" + str(
                                        uuid) + "/error/9",
                                    "uuid": str(uuid)
                                }
                        }
                    return Response(json.dumps(unauthorizedError), status=401)
                basic_auth = request.headers.get("Authorization").split(" ")
                basic_auth = b64.b64decode(basic_auth[1]).decode("utf-8").split(":")
                auth_password = basic_auth[1]
                auth_email = basic_auth[0]
                dataDfUuid = dataObj.get_df_uuid()
                incrUuid = 0
                compareUuid = dataDfUuid['uuid'].isin([uuid])
                for boolUuid in compareUuid:
                    if boolUuid == False:
                        incrUuid = incrUuid + 1
                    else:
                        if dataDfUuid['password'].get(incrUuid) == auth_password and dataDfUuid['email'].get(
                                incrUuid) == auth_email:
                            if "application/json" in request.headers["Content-Type"]:
                                if request.get_json()["sex"] == "Mr" or request.get_json()["sex"] == "Ms" or \
                                        request.get_json()[
                                            "sex"] == "Mrs":
                                    sex = request.get_json()["sex"]
                                elif request.get_json()["sex"] != "":
                                    badRequestError = \
                                        {
                                            "problem": {
                                                "type": "https://httpstatuses.com/400",
                                                "summary": "Failed to decode JSON object: Expecting 'Mr', 'Ms' or 'Mrs' in value "
                                                           "or the Json "
                                                           "key 'sex'.",
                                                "status": 400,
                                                "error_code": 10,
                                                "details": "The given input for 'sex' is not allowed.",
                                                "information": "http://127.0.0.1:5000/api/v1/users/error/10"
                                            }
                                        }
                                    return Response(json.dumps(badRequestError), status=400)
                                if request.get_json()["firstName"] != "":
                                    firstName = request.get_json()["firstName"]
                                if request.get_json()["lastName"] != "":
                                    lastName = request.get_json()["lastName"]
                                if request.get_json()["address"] != "":
                                    address = request.get_json()["address"]
                                if request.get_json()["city"] != "":
                                    city = request.get_json()["city"]
                                if request.get_json()["zipCode"] != "":
                                    zipCode = request.get_json()["zipCode"]
                                if request.get_json()["phoneNumber"] != "":
                                    phoneNumber = request.get_json()["phoneNumber"]
                                if request.get_json()["email"] != "":
                                    email = request.get_json()["email"]
                                if request.get_json()["password"] != "":
                                    password = request.get_json()["password"]

                                dataDfUuid = dataObj.get_df_uuid()
                                incrUuid = 0
                                incrEmail = 0
                                compareUuid = dataDfUuid['uuid'].isin([uuid])
                                compareEmail = dataDfUuid['email'].isin([email])
                                for boolUuid in compareUuid:
                                    if boolUuid == False:
                                        incrUuid = incrUuid + 1
                                    else:
                                        for boolEmail in compareEmail:
                                            if boolEmail == False:
                                                incrEmail = incrEmail + 1
                                            elif email != dataDfUuid.at[incrUuid, 'email']:
                                                conflictError = \
                                                    {
                                                        "problem":
                                                            {
                                                                "type": "https://httpstatuses.com/409",
                                                                "summary": "The given e-mail is already used by another user.",
                                                                "status": 409,
                                                                "error_code": 11,
                                                                "details": "E-mail is already used!",
                                                                "information": "http://127.0.0.1:5000/api/v1/users/" + str(
                                                                    uuid) + "/error/11",
                                                                "uuid": str(uuid)
                                                            }
                                                    }
                                                return Response(json.dumps(conflictError), status=409)
                                        if request.get_json()["sex"] == "Mr" or request.get_json()["sex"] == "Ms" or \
                                                request.get_json()[
                                                    "sex"] == "Mrs":
                                            dataDfUuid.at[incrUuid, "sex"] = sex
                                        if request.get_json()["firstName"] != "":
                                            dataDfUuid.at[incrUuid, "firstName"] = firstName
                                        if request.get_json()["lastName"] != "":
                                            dataDfUuid.at[incrUuid, "lastName"] = lastName
                                        if request.get_json()["address"] != "":
                                            dataDfUuid.at[incrUuid, "address"] = address
                                        if request.get_json()["city"] != "":
                                            dataDfUuid.at[incrUuid, "city"] = city
                                        if request.get_json()["zipCode"] != "":
                                            dataDfUuid.at[incrUuid, "zipCode"] = zipCode
                                        if request.get_json()["phoneNumber"] != "":
                                            dataDfUuid.at[incrUuid, "phoneNumber"] = phoneNumber
                                        if request.get_json()["email"] != "":
                                            dataDfUuid.at[incrUuid, "email"] = email
                                        if request.get_json()["password"] != "":
                                            dataDfUuid.at[incrUuid, "password"] = password
                                        #dataObj.set_df_uuid(dataDfUuid)
                                        replacedDfValue = dataDfUuid.drop(columns=["password"]).iloc[[incrUuid]].to_json(orient="records",
                                                                                              default_handler=str).replace(
                                            "[", "")
                                        responseDfJson = replacedDfValue.replace("]", "")
                                        response = Response(responseDfJson, mimetype='application/json',
                                                            status=200)
                                        response.headers["location"] = "/api/v1/users/" + str(uuid)
                                        return response
                            else:
                                unsupportetMediaTypeError = \
                                    {
                                        "problem":
                                            {
                                                "type": "https://httpstatuses.com/415",
                                                "summary": "The supplied Content-Type header is not supported."
                                                           "Only application/json is supported as Content-Type.",
                                                "status": 415,
                                                "error_code": 12,
                                                "details": "The message has not been sent in json. The Api supports only json.",
                                                "information": "http://127.0.0.1:5000/api/v1/users/" + str(
                                                    uuid) + "/error/12",
                                                "uuid": str(uuid)
                                            }
                                    }
                                return Response(json.dumps(unsupportetMediaTypeError), status=415)
                        else:
                            unauthorizedError = \
                                {
                                    "problem":
                                        {
                                            "type": "https://httpstatuses.com/401",
                                            "summary": "The supplied username(e-mail) or password does not match the "
                                                       "information associated with the uuid in the system.",
                                            "status": 401,
                                            "error_code": 13,
                                            "details": "Invalid username(e-mail) or password.",
                                            "information": "http://127.0.0.1:5000/api/v1/users/" + str(
                                                uuid) + "/error/13",
                                            "uuid": str(uuid)
                                        }
                                }
                            return Response(json.dumps(unauthorizedError), status=401)
                if incrUuid == int(len(compareUuid)):
                    userNotFoundError = \
                        {
                            "problem":
                                {
                                    "type": "https://httpstatuses.com/404",
                                    "summary": "No user could be found in the system with the given Universally Unique Identifier (UUID).",
                                    "status": 404,
                                    "error_code": 14,
                                    "details": "User was not found.",
                                    "information": "http://127.0.0.1:5000/api/v1/users/" + str(uuid) + "/error/14",
                                    "uuid": str(uuid)
                                }
                        }
                    return Response(json.dumps(userNotFoundError), status=404)
            else:
                notAcceptableError = \
                    {
                        "problem":
                            {
                                "type": "https://httpstatuses.com/406",
                                "summary": "Only application/json or */* is supported in the Accept header.",
                                "status": 406,
                                "error_code": 15,
                                "details": "The supplied Accept header is not supported.",
                                "information": "http://127.0.0.1:5000/api/v1/users/" + str(uuid) + "/error/15",
                                "uuid": str(uuid)
                            }
                    }
                return Response(json.dumps(notAcceptableError), status=406)
        except Exception as e:
            splittedE = str(e).split(": ", 1)[1]
            eStatus = str(e).split()
            catchAllErrors = \
                {
                    "problem":
                        {
                            "type": "https://httpstatuses.com/" + eStatus[0],
                            "summary": splittedE,
                            "status": int(eStatus[0]),
                            "error_code": 16,
                            "details": "Error was triggered while processing the request.",
                            "information": "http://127.0.0.1:5000/api/v1/users/" + str(uuid) + "/error/16",
                            "uuid": str(uuid)
                        }
                }
            return Response(json.dumps(catchAllErrors), status=int(eStatus[0]))


@api.doc(responses={
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    406: "Not Acceptable"
})
@api.route("/users/<string:uuid>")
class deleteUser(Resource):
    def delete(self, uuid):
        try:
            if request.headers.get('accept') == "*/*" or request.headers.get('accept') == "application/json":
                basic_auth = request.headers.get("Authorization").split(" ")
                basic_auth = b64.b64decode(basic_auth[1]).decode("utf-8").split(":")
                password = basic_auth[1]
                email = basic_auth[0]
                dataDfUuid = dataObj.get_df_uuid()
                incrUuid = 0
                compareUuid = dataDfUuid['uuid'].isin([uuid])
                for boolUuid in compareUuid:
                    if boolUuid == False:
                        incrUuid = incrUuid + 1
                    else:
                        if dataDfUuid['password'].get(incrUuid) == password:
                            dataObj.set_df_uuid(dataDfUuid.drop(incrUuid))
                            response = Response("{\"message\": \"User was successfully deleted.\"}",
                                                mimetype='application/json',
                                                status=200)
                            response.headers["location"] = "/api/v1/users"
                            return response
                        else:
                            unauthorizedError = \
                                {
                                    "problem":
                                        {
                                            "type": "https://httpstatuses.com/401",
                                            "summary": "The supplied username(e-mail) or password does not match the "
                                                       "information associated with the uuid in the system.",
                                            "status": 401,
                                            "error_code": 17,
                                            "details": "Invalid username(e-mail) or password.",
                                            "information": "http://127.0.0.1:5000/api/v1/users/" + str(
                                                uuid) + "/error/17",
                                            "uuid": str(uuid)
                                        }
                                }
                            return Response(json.dumps(unauthorizedError), status=401)
                if incrUuid == int(len(compareUuid)):
                    userNotFoundError = \
                        {
                            "problem":
                                {
                                    "type": "https://httpstatuses.com/404",
                                    "summary": "No user could be found in the system with the given Universally Unique Identifier (UUID).",
                                    "status": 404,
                                    "error_code": 18,
                                    "details": "User was not found.",
                                    "information": "http://127.0.0.1:5000/api/v1/users/" + str(uuid) + "/error/18",
                                    "uuid": str(uuid)
                                }
                        }
                    return Response(json.dumps(userNotFoundError), status=404)
            else:
                notAcceptableError = \
                    {
                        "problem":
                            {
                                "type": "https://httpstatuses.com/406",
                                "summary": "Only application/json or */* is supported in the Accept header.",
                                "status": 406,
                                "error_code": 19,
                                "details": "The supplied Accept header is not supported.",
                                "information": "http://127.0.0.1:5000/api/v1/users/" + str(uuid) + "/error/19",
                                "uuid": str(uuid)
                            }
                    }
                return Response(json.dumps(notAcceptableError), status=406)
        except Exception as e:
            splittedE = str(e).split(": ", 1)[1]
            eStatus = str(e).split()
            catchAllErrors = \
                {
                    "problem":
                        {
                            "type": "https://httpstatuses.com/" + eStatus[0],
                            "summary": splittedE,
                            "status": int(eStatus[0]),
                            "error_code": 20,
                            "details": "Error was triggered while processing the request.",
                            "information": "http://127.0.0.1:5000/api/v1/users/" + str(uuid) + "/error/20",
                            "uuid": str(uuid)
                        }
                }
            return Response(json.dumps(catchAllErrors), status=int(eStatus[0]))


if __name__ == '__main__':
    app.run()

"""
nochmal Fragen:
- bei delete UUID im location header?

- Passwort bei GET auch zurückgeben oder dort Passwort und Username(email) nicht zurückgeben?
- Passwort und Username(email) bei POST also bei dem Anlegen des Users in Authorization header oder in Body? 
( Als Ergebnis wird bisher der Angelegte User zurückgeben, aber ohne email und passwort)
- Bei PUT, Passwort und Username(email) beim Aktualisieren der User Daten in Authorization header oder in Body?
- Bei Delete steht nun der Username und das Passwort im Authorization header.
- Location Header auch bei Error?

"""
