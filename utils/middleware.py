from django.http import JsonResponse


class CommonResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin'):
            return self.get_response(request)
        if request.path.startswith('/media'):
            return self.get_response(request)
        # Get the response object from the view
        response = self.get_response(request)

        # Modify the response object as necessary
        if response.status_code == 404:
            response = JsonResponse(
                {
                  "status": "error",
                  "message": "Details not found",
                  "data": None
                },
                status=404
              )
        elif response.status_code == 500:
            response = JsonResponse(
                {
                  "status": "error",
                  "message": "Internal server error",
                  "data": None
                },
                status=500
              )
        elif response.status_code == 400:
            error_message = getattr(
                response,
                'error_message',
                response.data
            )
            response = JsonResponse(
                {
                  "status": "error",
                  "message": error_message,
                  "data": None
                },
                status=400
              )
        elif response.status_code == 200:
            success_message = getattr(
                response,
                'success_message',
                'Successfull'
            )
            response = JsonResponse(
                {
                  "status": "success",
                  "message": success_message,
                  "data": response.data
                },
                status=200
            )
        elif response.status_code == 403:
            error_message = getattr(
                response,
                'error_message',
                'You have not permission to perform this Action.'
            )
            response = JsonResponse(
                {
                  "status": "error",
                  "message": error_message,
                  "data": None
                },
                status=400
              )
        return response
