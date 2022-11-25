from utils.crud import create_object


def create_useful_question(instance, validated_data):
    data = {
        'user': instance,
        **validated_data
    }
    create_object(app_label='auth_user', model_name='UsefulQuestion', validated_data=data)
