from django.db.models import Aggregate, DecimalField, BooleanField, FloatField, IntegerField


class BaseAggregate(Aggregate):

    def __rand__(self, other):
        pass

    def __ror__(self, other):
        pass


class GetProductPriceAggregate(BaseAggregate):

    function = 'get_product_price'
    template = "%(function)s(%(current_product_id)s, '%(city_slug)s', '%(current_storehouse_type)s')"
    output_field = DecimalField()

    def __init__(self, current_product_id, city_slug, current_storehouse_type):
        super().__init__(current_product_id=current_product_id, city_slug=city_slug,
                         current_storehouse_type=current_storehouse_type)


class GetProductRestAggregate(BaseAggregate):

    function = 'get_product_rest'
    template = "%(function)s(%(current_product_id)s, '%(city_slug)s')"
    output_field = DecimalField()

    def __init__(self, current_product_id, city_slug):
        super().__init__(current_product_id=current_product_id, city_slug=city_slug)


class GetProductIsFavouriteAggregate(BaseAggregate):

    function = 'get_product_is_favourite'
    template = "%(function)s(%(current_product_id)s, %(current_user_id)d)"
    output_field = BooleanField()

    def __init__(self, current_product_id, current_user_id):
        super().__init__(current_product_id=current_product_id, current_user_id=current_user_id)


class GetProductPopularityAggregate(BaseAggregate):

    function = 'get_product_popularity'
    template = "%(function)s(%(current_product_id)s)"
    output_field = IntegerField()

    def __init__(self, current_product_id):
        super().__init__(current_product_id=current_product_id)


class GetProductRatingAggregate(GetProductPopularityAggregate):

    function = 'get_product_rating'
    output_field = FloatField()


class GetProductCommentsAggregate(GetProductPopularityAggregate):

    function = 'get_product_comments'
    output_field = IntegerField()

