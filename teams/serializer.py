from rest_framework import serializers

from common.models import Profile
from common.serializer import ProfileSerializer,UserSerializer
from teams.models import Teams


class TeamsSerializer(serializers.ModelSerializer):
    users = ProfileSerializer(read_only=True, many=True)
    created_by = UserSerializer()

    class Meta:
        model = Teams
        fields = (
            "id",
            "name",
            "description",
            "users",
            "created_at",
            "created_by",
            "created_on_arrow",
        )


class TeamCreateSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Profile.objects.all(), required=False
    )

    def __init__(self, *args, **kwargs):
        request_obj = kwargs.pop("request_obj", None)
        super().__init__(*args, **kwargs)
        self.org = request_obj.profile.org

        self.fields["name"].required = True
        self.fields["description"].required = False

    def validate_name(self, name):
        if self.instance:
            if (
                Teams.objects.filter(name__iexact=name, org=self.org)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise serializers.ValidationError("Team already exists with this name")
        else:
            if Teams.objects.filter(name__iexact=name, org=self.org).exists():
                raise serializers.ValidationError("Team already exists with this name")
        return name

    def create(self, validated_data):
        users = validated_data.pop('users', [])
        team = Teams.objects.create(org=self.org, **validated_data)
        if users:
            team.users.set(users)
        return team

    class Meta:
        model = Teams
        fields = (
            "name",
            "description",
            "created_at",
            "created_by",
            "created_on_arrow",
            "users",  # Removed "org" from fields as it's handled in create method
        )


class TeamswaggerCreateSerializer(serializers.ModelSerializer):

      
    class Meta:
        model = Teams
        fields = (
            "name",
            "description",
            "users",
        )