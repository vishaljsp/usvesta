# from django.http import HttpResponseForbidden

# BLOCKED_AGENTS = [
#     "scrapy", "curl", "httpclient", "python-requests",
#     "wget", "libwww", "httpunit", "nmap"
# ]

# class BlockBotsMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         user_agent = request.META.get("HTTP_USER_AGENT", "").lower()

#         if any(bot in user_agent for bot in BLOCKED_AGENTS):
#             return HttpResponseForbidden("🚫 Access Denied")

#         return self.get_response(request)
