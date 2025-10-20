from rest_framework import serializers
from .models import AnalyzedString
from .utils import analyze_string

class AnalyzedStringSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AnalyzedString
        fields = [
            'id',
            'value',
            'created_at',
            'properties',
        ]
        read_only_fields = ['id', 'created_at', 'properties']
    def get_properties(self, obj):
        return {
            "length": obj.length,
            "is_palindrome": obj.is_palindrome,
            "unique_characters": obj.unique_characters,
            "word_count": obj.word_count,
            "character_frequency_map": obj.character_frequency_map,
            "sha256_hash": obj.id,
        }
    def validate_value(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Input must be a string.")
        if value.strip() == "":
            raise serializers.ValidationError("Input string cannot be empty.")
        return value
    def create(self, validated_data):
        input_string = validated_data['value']
        analysis_result = analyze_string(input_string)
        if AnalyzedString.objects.filter(id=analysis_result['sha256_hash']).exists():
            # raise a proper ValidationError so the view can catch and format it
            raise serializers.ValidationError("String already exists in the system")
        analyzed_string_instance = AnalyzedString.objects.create(
            id=analysis_result['sha256_hash'],
            value=analysis_result['value'],
            length=analysis_result['length'],
            is_palindrome=analysis_result['is_palindrome'],
            unique_characters=analysis_result['unique_characters'],
            word_count=analysis_result['word_count'],
            character_frequency_map=analysis_result['character_frequency_map'],
        )
        return analyzed_string_instance