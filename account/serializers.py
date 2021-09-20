from rest_framework import serializers

from account.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(label='비밀번호', max_length=128, required=True, style={'input_type': 'password'},
                                     write_only=True)

    class Meta:
        model = User
        exclude = ('is_active', 'is_superuser', 'is_staff', 'date_joined',
                   'last_login', 'groups', 'user_permissions')

    def create(self, validated_data):
        field_names = list(self.get_fields().keys())[1:]  # get_fields() is OrderedDict(), so id's index is 0
        validated_dict = {field: validated_data[field] for field in field_names}
        validated_dict['is_active'] = False
        user = User.objects.create_user(**validated_dict)
        return user
