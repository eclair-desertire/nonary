
from utils.crud import create_object


def set_viewed_story(instance, user):
    return create_object(app_label='main_page', model_name='UserViewedStory',
                         validated_data={'story': instance, 'user': user})
