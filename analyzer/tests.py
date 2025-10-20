from urllib import response
from django.urls import reverse
from django.test import TestCase
from .models import AnalyzedString
from rest_framework.test import APIClient, APITestCase

# Create your tests here.
class AnalyzedStringModelTest(TestCase):
    def setUp(self):
        self.url = reverse('create-string')

    def test_analyzed_string_creation(self):
        response = self.client.post(self.url, {
            "value": "race car",
        }, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(AnalyzedString.objects.count(), 1)
        analyzed_string = AnalyzedString.objects.first()
        self.assertEqual(analyzed_string.value, "race car")
        self.assertEqual(analyzed_string.length, 8)
        self.assertEqual(analyzed_string.is_palindrome, True)
        self.assertEqual(analyzed_string.unique_characters, 4)
        self.assertEqual(analyzed_string.word_count, 2)
        self.assertEqual(analyzed_string.character_frequency_map["r"], 2)

    def test_duplicate_string_creation(self):
        response1 = self.client.post(self.url, {
            "value": "hello",
        }, content_type='application/json')
        self.assertEqual(response1.status_code, 201)
        response2 = self.client.post(self.url, {
            "value": "hello",
        }, content_type='application/json')
        # view returns 409 Conflict for duplicate strings
        self.assertEqual(response2.status_code, 409)
        self.assertIn("String already exists in the system", str(response2.data))
    def test_empty_string_creation(self):
        response = self.client.post(self.url, {
            "value": "   ",
        }, content_type='application/json')
        # view returns 422 Unprocessable Entity for empty input
        self.assertEqual(response.status_code, 422)
        self.assertIn("Input string cannot be empty.", str(response.data))
    def test_non_string_input(self):
        response = self.client.post(self.url, {
            "value": 12345,
        }, content_type='application/json')
        # view returns 422 Unprocessable Entity for non-string input
        self.assertEqual(response.status_code, 422)
        self.assertIn("Input must be a string.", str(response.data))
    def test_retrieve_analyzed_string(self):
        create_response = self.client.post(self.url, {
            "value": "madam",
        }, content_type='application/json')
        self.assertEqual(create_response.status_code, 201)
        retrieve_url = reverse('get-string', args=["madam"])
        retrieve_response = self.client.get(retrieve_url)
        self.assertEqual(retrieve_response.status_code, 200)
        self.assertEqual(retrieve_response.data['value'], "madam")
        self.assertEqual(retrieve_response.data['properties']['is_palindrome'], True)
    def test_delete_analyzed_string(self):
        create_response = self.client.post(self.url, {
            "value": "teststring",
        }, content_type='application/json')
        self.assertEqual(create_response.status_code, 201)
        delete_url = reverse('get-string', args=["teststring"])
        delete_response = self.client.delete(delete_url)
        self.assertEqual(delete_response.status_code, 204)
        retrieve_response = self.client.get(delete_url)
        self.assertEqual(retrieve_response.status_code, 404)
    def test_list_analyzed_strings_with_filters(self):
        strings = ["level", "hello world", "A man a plan a canal Panama", "test"]
        for s in strings:
            self.client.post(self.url, {
                "value": s,
            }, content_type='application/json')
        list_url = reverse('list-strings')
        response = self.client.get(list_url, {
            "is_palindrome": True
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 2)  
        self.assertIn("level", [item['value'] for item in response.data['data']])
        self.assertIn("A man a plan a canal Panama", [item['value'] for item in response.data['data']])
    def test_list_analyzed_strings_with_length_filters(self):
        strings = ["level", "hello world", "A man a plan a canal Panama", "test"]
        list_url = reverse('list-strings')
        for s in strings:
            self.client.post(self.url, {
                "value": s,
            }, content_type='application/json')
        response = self.client.get(list_url, {
            "min_length": 5,
            "max_length": 35
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 3)  
        self.assertIn("hello world", [item['value'] for item in response.data['data']])
        self.assertIn("A man a plan a canal Panama", [item['value'] for item in response.data['data']])
    def test_list_analyzed_strings_with_invalid_filters(self):
        strings = ["level", "hello world", "A man a plan a canal Panama", "test"]
        list_url = reverse('list-strings')
        for s in strings:
            self.client.post(self.url, {
                "value": s,
            }, content_type='application/json')
        response = self.client.get(list_url, {
            "min_length": 20,
            "max_length": 10
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("min_length cannot be greater than max_length", str(response.data))
    def test_list_analyzed_strings_with_malformed_filters(self):
        strings = ["level", "hello world", "A man a plan a canal Panama", "test"]
        list_url = reverse('list-strings')
        for s in strings:
            self.client.post(self.url, {
                "value": s,
            }, content_type='application/json')
        response = self.client.get(list_url, {
            "is_palindrome": "notabool"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid boolean for is_palindrome", str(response.data))
    def test_list_analyzed_strings_with_malformed_length_integer_filters(self):
        strings = ["level", "hello world", "A man a plan a canal Panama", "test"]
        list_url = reverse('list-strings')
        for s in strings:
            self.client.post(self.url, {
                "value": s,
            }, content_type='application/json')
        response = self.client.get(list_url, {
            "min_length": "notanint"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid integer for min_length", str(response.data))   
    def test_list_analyzed_strings_with_malformed_word_count_integer_filters(self):
        strings = ["level", "hello world", "A man a plan a canal Panama", "test"]
        list_url = reverse('list-strings')
        for s in strings:
            self.client.post(self.url, {
                "value": s,
            }, content_type='application/json')
        response = self.client.get(list_url, {
            "word_count": "notanint"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid integer for word_count", str(response.data))
    def test_list_analyzed_strings_with_malformed_contains_character_filter(self):
        strings = ["level", "hello world", "A man a plan a canal Panama", "test"]
        list_url = reverse('list-strings')
        for s in strings:
            self.client.post(self.url, {
                "value": s,
            }, content_type='application/json')
        response = self.client.get(list_url, {
            "contains_character": 123
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("[]", str(response.data))
        self.assertEqual(len(response.data['data']), 0) 

    # Natural language filter endpoint tests
    def test_nl_filter_single_word_palindromic(self):
        # create a few strings
        samples = ["level", "rotor", "hello world"]
        for s in samples:
            self.client.post(self.url, {"value": s}, content_type='application/json')

        nl_url = reverse('nl-filter')
        response = self.client.get(nl_url, {"query": "all single word palindromic strings"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['interpreted_query']['parsed_filters']['word_count'], 1)
        self.assertTrue(response.data['interpreted_query']['parsed_filters']['is_palindrome'])
        self.assertGreaterEqual(response.data['count'], 2)

    def test_nl_filter_length_and_contains(self):
        samples = ["abcdefghijklmnopqrstuvwxyz", "short", "zzzzzzzzzzz"]
        for s in samples:
            self.client.post(self.url, {"value": s}, content_type='application/json')

        nl_url = reverse('nl-filter')
        response = self.client.get(nl_url, {"query": "strings longer than 10 characters"})
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['count'], 2)
        self.assertIn('min_length', response.data['interpreted_query']['parsed_filters'])

    def test_nl_filter_contains_letter_z(self):
        samples = ["amazing", "buzz", "fizz"]
        for s in samples:
            self.client.post(self.url, {"value": s}, content_type='application/json')
        nl_url = reverse('nl-filter')
        response = self.client.get(nl_url, {"query": "strings containing the letter z"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('contains_character', response.data['interpreted_query']['parsed_filters'])

    def test_nl_filter_unable_to_parse(self):
        nl_url = reverse('nl-filter')
        response = self.client.get(nl_url, {"query": "gibberish qwerty asdf"})
        self.assertEqual(response.status_code, 400)

    def test_nl_filter_conflicting_filters(self):
        # craft a query that will produce conflicting min/max lengths
        nl_url = reverse('nl-filter')
        # the parser currently won't synthesize conflicting numeric filters except via explicit numbers
        response = self.client.get(nl_url, {"query": "strings longer than 20 and shorter than 10"})
        self.assertEqual(response.status_code, 422)
