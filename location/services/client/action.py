

def select_city(user, city):
    if user.is_authenticated:
        user.city = city
        user.save()
    return city
