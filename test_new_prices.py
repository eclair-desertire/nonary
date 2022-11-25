from shop.models import Product, ProductPrice, Rest

products = Product.objects.all()


def save_prices():
    for good in products:
        prices = ProductPrice.objects.filter(product=good)
        prices_dict = {}
        for price in prices:
            cities = price.storehouse.cities.all()
            for city in cities:
                prices_dict.update({
                     f"{city.slug}_{price.storehouse.storehouse_type}": int(price.price)
                })
        good.prices_dict = prices_dict
        good.save()


def save_rests():
    for good in products:
        rests = Rest.objects.filter(product=good)
        rests_dict = {}
        for rest in rests:
            cities = rest.storehouse.cities.all()
            for city in cities:
                rests_dict.update({
                     f"{city.slug}_{rest.storehouse.storehouse_type}": rest.quantity
                })
        good.rests_dict = rests_dict
        good.save()
