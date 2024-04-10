from django.contrib import messages


MSG = (
    
)


class DemoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Code to be executed for each request before
        # the view (and later middleware) are called.
        demo_message_exists = False
        storage = messages.get_messages(request)
        for message in storage:
            if str(message) == MSG:
                demo_message_exists = True
        storage.used = False
        if not demo_message_exists:
            messages.add_message(request, messages.WARNING, MSG)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
