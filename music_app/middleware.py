class MobileUploadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is on a mobile device
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        is_mobile = any(device in user_agent for device in ['iphone', 'android', 'mobile'])
        
        # Add to request for template context
        request.is_mobile_device = is_mobile
        
        response = self.get_response(request)
        return response