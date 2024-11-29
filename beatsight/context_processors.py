def redirect_to(request):
    # Get the 'next' parameter from the request, default to '/'
    redirect_to = request.GET.get('next', '/dashbaord')
    return {'redirect_to': redirect_to}
