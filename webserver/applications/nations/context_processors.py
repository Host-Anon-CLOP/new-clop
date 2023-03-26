def nations(request):
    if not request.user.is_authenticated:
        return {}

    active_nation = request.user.nation
    return {
        'nation': active_nation,
    }
