from rest_framework.response import Response 

class CustomResponse():
    '''
    A Custom Response Class
    '''
    def Success(data, status=200, headers=None):
        data1 = {
            "data": data,
            "errors": [],
            "status": status,
            "message": "Success"
        }
        return Response(data1, status, headers)
    
    def Failure(error, status=400, headers=None):
        data1 = {
            "errors": error,
            "data": [],
            "status": status,
            "message": "Failed"
        }
        return Response(data1, status, headers)
