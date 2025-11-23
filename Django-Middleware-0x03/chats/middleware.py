import logging
from datetime import datetime, time
from collections import defaultdict
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='requests.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class RequestLoggingMiddleware(MiddlewareMixin):
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        current_time = datetime.now().time()
        start_time = time(9, 0)
        end_time = time(18, 0)
        
        if request.path.startswith('/api/') and not request.path.startswith('/api/auth/'):
            if not (start_time <= current_time <= end_time):
                return JsonResponse(
                    {
                        'error': 'Access denied',
                        'message': 'Chat access is only allowed between 9:00 AM and 6:00 PM'
                    },
                    status=403
                )
        
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware(MiddlewareMixin):
    
    message_counts = defaultdict(list)
    MAX_MESSAGES = 5
    TIME_WINDOW = 60
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        if request.method == 'POST' and '/api/messages' in request.path:
            ip_address = self.get_client_ip(request)
            current_time = datetime.now().timestamp()
            
            self.message_counts[ip_address] = [
                timestamp for timestamp in self.message_counts[ip_address]
                if current_time - timestamp < self.TIME_WINDOW
            ]
            
            if len(self.message_counts[ip_address]) >= self.MAX_MESSAGES:
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded',
                        'message': f'You can only send {self.MAX_MESSAGES} messages per minute'
                    },
                    status=429
                )
            
            self.message_counts[ip_address].append(current_time)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolepermissionMiddleware(MiddlewareMixin):
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        if request.user.is_authenticated:
            if request.method == 'DELETE' and request.path.startswith('/api/'):
                user_role = getattr(request.user, 'role', None)
                
                if not (request.user.is_superuser or user_role in ['admin', 'moderator']):
                    return JsonResponse(
                        {
                            'error': 'Permission denied',
                            'message': 'Only administrators and moderators can perform delete operations'
                        },
                        status=403
                    )
        
        response = self.get_response(request)
        return response
