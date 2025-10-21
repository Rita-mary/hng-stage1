from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import AnalyzedStringSerializer
from .models import AnalyzedString
from rest_framework import serializers
from .utils import analyze_string , parse_bool, parse_int
from .utils import parse_natural_language_query, NaturalLanguageParseError, NaturalLanguageConflictError
# Create your views here.

class AnalyzedStringCreateView(generics.CreateAPIView):
    serializer_class = AnalyzedStringSerializer

    def create(self,request,*args, **kwargs):
        raw_value = request.data.get('value', None)
        if raw_value is not None and not isinstance(raw_value, str):
            return Response({'error': 'Input must be a string.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if isinstance(raw_value, str) and raw_value.strip() == '':
            return Response({'error': 'Input string cannot be empty.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        serializer= self.get_serializer(data = request.data)
        try:
            analysis = analyze_string(raw_value) if raw_value is not None else None
            if analysis and AnalyzedString.objects.filter(id=analysis['sha256_hash']).exists():
                return Response({'error': 'String already exists in the system'}, status=status.HTTP_409_CONFLICT)
        except Exception:
            pass

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except serializers.ValidationError as e:
            detail_str = str(e.detail)
            if 'String already exists in the system' in detail_str:
                return Response({'error': 'String already exists in the system'}, status=status.HTTP_409_CONFLICT)
            if 'Input must be a string.' in detail_str:
                return Response({'error': 'Input must be a string.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if 'Input string cannot be empty.' in detail_str:
                return Response({'error': 'Input string cannot be empty.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            return Response({'error': detail_str}, status=status.HTTP_400_BAD_REQUEST)
            
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class StringRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    serializer_class = AnalyzedStringSerializer
    lookup_field = 'value'
    queryset = AnalyzedString.objects.all()

class ListAnalyzedStringsView(generics.ListAPIView):
    serializer_class = AnalyzedStringSerializer

    def get_queryset(self):
        qs = AnalyzedString.objects.all()
        qp = self.request.query_params


        if 'is_palindrome' in qp:
            try:
                is_palindrome = parse_bool(qp['is_palindrome'])
                qs = qs.filter(is_palindrome=is_palindrome)
            except ValueError:
                raise serializers.ValidationError("Invalid boolean for is_palindrome")
            
        if 'min_length' and 'max_length' in qp:
            try:
                min_length = parse_int(qp['min_length'])
                max_length = parse_int(qp['max_length'])
                if min_length > max_length:
                    raise serializers.ValidationError("min_length cannot be greater than max_length")
            except ValueError:
                raise serializers.ValidationError("Invalid integer for min_length or max_length")

        if 'min_length' in qp:
            try:
                min_length = parse_int(qp['min_length'])
                qs = qs.filter(length__gte=min_length)
            except ValueError:
                raise serializers.ValidationError("Invalid integer for min_length")

        if 'max_length' in qp:
            try:
                max_length = parse_int(qp['max_length'])
                qs = qs.filter(length__lte=max_length)
            except ValueError:
                raise serializers.ValidationError("Invalid integer for max_length")

        if 'contains_character' in qp:
            substring = qp['contains_character']
            qs = qs.filter(value__icontains=substring)

        if 'word_count' in qp:
            try:
                word_count = parse_int(qp['word_count'])
                qs = qs.filter(word_count=word_count)
            except ValueError:
                raise serializers.ValidationError("Invalid integer for word_count")
        return qs
    
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        for val in request.query_params:
            if val not in ['is_palindrome', 'min_length', 'max_length', 'contains_character', 'word_count']:
                return Response({'error': f'Invalid filter parameter: {val}'}, status=status.HTTP_400_BAD_REQUEST)
        applied = {k: request.query_params[k] for k in request.query_params}

        return Response({
            "data" : serializer.data,
            "count": qs.count(),
            "filter_applied": applied
        })


class NaturalLanguageFilterView(generics.GenericAPIView):
    serializer_class = AnalyzedStringSerializer

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query')
        try:
            interpreted = parse_natural_language_query(query)
        except NaturalLanguageParseError:
            return Response({'error': 'Unable to parse natural language query'}, status=status.HTTP_400_BAD_REQUEST)
        except NaturalLanguageConflictError:
            return Response({'error': 'Query parsed but resulted in conflicting filters'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        filters = interpreted['parsed_filters']
        qs = AnalyzedString.objects.all()

        if 'word_count' in filters:
            qs = qs.filter(word_count=filters['word_count'])
        if 'is_palindrome' in filters:
            qs = qs.filter(is_palindrome=filters['is_palindrome'])
        if 'min_length' in filters:
            qs = qs.filter(length__gte=filters['min_length'])
        if 'max_length' in filters:
            qs = qs.filter(length__lte=filters['max_length'])
        if 'contains_character' in filters:
            qs = qs.filter(value__icontains=filters['contains_character'])

        serializer = self.get_serializer(qs, many=True)
        return Response({
            'data': serializer.data,
            'count': qs.count(),
            'interpreted_query': interpreted,
        })

class ListCreateAnalyzedStringsView(generics.ListCreateAPIView):
    serializer_class = AnalyzedStringSerializer

    def get_queryset(self):
        qs = AnalyzedString.objects.all()
        qp = self.request.query_params

        if 'is_palindrome' in qp:
            try:
                is_palindrome = parse_bool(qp['is_palindrome'])
                qs = qs.filter(is_palindrome=is_palindrome)
            except ValueError:
                raise serializers.ValidationError("Invalid boolean for is_palindrome")

        if 'min_length' in qp:
            try:
                min_length = parse_int(qp['min_length'])
                qs = qs.filter(length__gte=min_length)
            except ValueError:
                raise serializers.ValidationError("Invalid integer for min_length")

        if 'max_length' in qp:
            try:
                max_length = parse_int(qp['max_length'])
                qs = qs.filter(length__lte=max_length)
            except ValueError:
                raise serializers.ValidationError("Invalid integer for max_length")

        if 'contains_character' in qp:
            substring = str(qp['contains_character'])
            qs = qs.filter(value__icontains=substring)

        if 'word_count' in qp:
            try:
                word_count = parse_int(qp['word_count'])
                qs = qs.filter(word_count=word_count)
            except ValueError:
                raise serializers.ValidationError("Invalid integer for word_count")

        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        # validate no unexpected query params
        allowed = {'is_palindrome', 'min_length', 'max_length', 'contains_character', 'word_count'}
        for val in request.query_params:
            if val not in allowed:
                return Response({'error': f'Invalid filter parameter: {val}'}, status=status.HTTP_400_BAD_REQUEST)
        applied = {k: request.query_params[k] for k in request.query_params}
        return Response({
            "data": serializer.data,
            "count": qs.count(),
            "filter_applied": applied
        })

    def create(self, request, *args, **kwargs):
        # simple pre-validation on raw payload to return the exact error codes/messages you prefer
        raw_value = request.data.get('value', None)
        if raw_value is None:
            return Response({'error': "Missing 'value' field"}, status=status.HTTP_400_BAD_REQUEST)
        if raw_value is not None and not isinstance(raw_value, str):
            return Response({'error': 'Input must be a string.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if isinstance(raw_value, str) and raw_value.strip() == '':
            return Response({'error': 'Input string cannot be empty.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        # pre-check duplicate by hashing the raw input so we can return 409 before attempting save
        try:
            analysis = analyze_string(raw_value)
            if AnalyzedString.objects.filter(id=analysis['sha256_hash']).exists():
                return Response({'error': 'String already exists in the system'}, status=status.HTTP_409_CONFLICT)
        except Exception:
            pass

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except serializers.ValidationError as e:
            detail_str = str(e.detail)
            if 'String already exists in the system' in detail_str:
                return Response({'error': 'String already exists in the system'}, status=status.HTTP_409_CONFLICT)
            if 'Input must be a string.' in detail_str:
                return Response({'error': 'Input must be a string.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if 'Input string cannot be empty.' in detail_str:
                return Response({'error': 'Input string cannot be empty.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            return Response({'error': detail_str}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

