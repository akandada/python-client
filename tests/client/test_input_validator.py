"""Unit tests for the input_validator module."""
#pylint: disable=protected-access,too-many-statements,no-self-use,line-too-long

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import logging

from splitio.client.factory import SplitFactory, get_factory
from splitio.client.client import CONTROL, Client
from splitio.client.manager import SplitManager
from splitio.client.key import Key
from splitio.storage import SplitStorage, EventStorage, ImpressionStorage, TelemetryStorage, \
    SegmentStorage
from splitio.models.splits import Split


class ClientInputValidationTests(object):
    """Input validation test cases."""

    def test_get_treatment(self, mocker):
        """Test get_treatment validation."""
        split_mock = mocker.Mock(spec=Split)
        default_treatment_mock = mocker.PropertyMock()
        default_treatment_mock.return_value = 'default_treatment'
        type(split_mock).default_treatment = default_treatment_mock
        conditions_mock = mocker.PropertyMock()
        conditions_mock.return_value = []
        type(split_mock).conditions = conditions_mock
        storage_mock = mocker.Mock(spec=SplitStorage)
        storage_mock.get.return_value = split_mock

        def _get_storage_mock(storage):
            return {
                'splits': storage_mock,
                'segments': mocker.Mock(spec=SegmentStorage),
                'impressions': mocker.Mock(spec=ImpressionStorage),
                'events': mocker.Mock(spec=EventStorage),
                'telemetry': mocker.Mock(spec=TelemetryStorage)
            }[storage]
        factory_mock = mocker.Mock(spec=SplitFactory)
        factory_mock._get_storage.side_effect = _get_storage_mock
        factory_destroyed = mocker.PropertyMock()
        factory_destroyed.return_value = False
        type(factory_mock).destroyed = factory_destroyed

        client = Client(factory_mock)
        client._logger = mocker.Mock()
        mocker.patch('splitio.client.input_validator._LOGGER', new=client._logger)

        assert client.get_treatment(None, 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed a null key, key must be a non-empty string.', 'get_treatment')
        ]

        client._logger.reset_mock()
        assert client.get_treatment('', 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an empty %s, %s must be a non-empty string.', 'get_treatment', 'key', 'key')
        ]

        client._logger.reset_mock()
        key = ''.join('a' for _ in range(0, 255))
        assert client.get_treatment(key, 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: %s too long - must be %s characters or less.', 'get_treatment', 'key', 250)
        ]

        client._logger.reset_mock()
        assert client.get_treatment(12345, 'some_feature') == 'default_treatment'
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: %s %s is not of type string, converting.', 'get_treatment', 'key', 12345)
        ]

        client._logger.reset_mock()
        assert client.get_treatment(float('nan'), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(float('inf'), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(True, 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment([], 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment('some_key', None) == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed a null %s, %s must be a non-empty string.', 'get_treatment', 'feature_name', 'feature_name')
        ]

        client._logger.reset_mock()
        assert client.get_treatment('some_key', 123) == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'feature_name', 'feature_name')
        ]

        client._logger.reset_mock()
        assert client.get_treatment('some_key', True) == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'feature_name', 'feature_name')
        ]

        client._logger.reset_mock()
        assert client.get_treatment('some_key', []) == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'feature_name', 'feature_name')
        ]

        client._logger.reset_mock()
        assert client.get_treatment('some_key', '') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an empty %s, %s must be a non-empty string.', 'get_treatment', 'feature_name', 'feature_name')
        ]

        client._logger.reset_mock()
        assert client.get_treatment('some_key', 'some_feature') == 'default_treatment'
        assert client._logger.error.mock_calls == []
        assert client._logger.warning.mock_calls == []

        client._logger.reset_mock()
        assert client.get_treatment(Key(None, 'bucketing_key'), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed a null %s, %s must be a non-empty string.', 'get_treatment', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(Key('', 'bucketing_key'), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an empty %s, %s must be a non-empty string.', 'get_treatment', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(Key(float('nan'), 'bucketing_key'), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(Key(float('inf'), 'bucketing_key'), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(Key(True, 'bucketing_key'), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(Key([], 'bucketing_key'), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(Key(12345, 'bucketing_key'), 'some_feature') == 'default_treatment'
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: %s %s is not of type string, converting.', 'get_treatment', 'matching_key', 12345)
        ]

        client._logger.reset_mock()
        key = ''.join('a' for _ in range(0, 255))
        assert client.get_treatment(Key(key, 'bucketing_key'), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: %s too long - must be %s characters or less.', 'get_treatment', 'matching_key', 250)
        ]

        client._logger.reset_mock()
        assert client.get_treatment(Key('mathcing_key', None), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed a null %s, %s must be a non-empty string.', 'get_treatment', 'bucketing_key', 'bucketing_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(Key('mathcing_key', True), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'bucketing_key', 'bucketing_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(Key('mathcing_key', []), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment', 'bucketing_key', 'bucketing_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(Key('mathcing_key', ''), 'some_feature') == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an empty %s, %s must be a non-empty string.', 'get_treatment', 'bucketing_key', 'bucketing_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment(Key('mathcing_key', 12345), 'some_feature') == 'default_treatment'
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: %s %s is not of type string, converting.', 'get_treatment', 'bucketing_key', 12345)
        ]

        client._logger.reset_mock()
        assert client.get_treatment('mathcing_key', 'some_feature', True) == CONTROL
        assert client._logger.error.mock_calls == [
            mocker.call('%s: attributes must be of type dictionary.', 'get_treatment')
        ]

        client._logger.reset_mock()
        assert client.get_treatment('mathcing_key', 'some_feature', {'test': 'test'}) == 'default_treatment'
        assert client._logger.error.mock_calls == []

        client._logger.reset_mock()
        assert client.get_treatment('mathcing_key', 'some_feature', None) == 'default_treatment'
        assert client._logger.error.mock_calls == []

        client._logger.reset_mock()
        assert client.get_treatment('mathcing_key', '  some_feature   ', None) == 'default_treatment'
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: feature_name \'%s\' has extra whitespace, trimming.', 'get_treatment', '  some_feature   ')
        ]

    def test_get_treatment_with_config(self, mocker):
        """Test get_treatment validation."""
        split_mock = mocker.Mock(spec=Split)
        default_treatment_mock = mocker.PropertyMock()
        default_treatment_mock.return_value = 'default_treatment'
        type(split_mock).default_treatment = default_treatment_mock
        conditions_mock = mocker.PropertyMock()
        conditions_mock.return_value = []
        type(split_mock).conditions = conditions_mock
        def _configs(treatment):
            return '{"some": "property"}' if treatment == 'default_treatment' else None
        split_mock.get_configurations_for.side_effect = _configs
        storage_mock = mocker.Mock(spec=SplitStorage)
        storage_mock.get.return_value = split_mock

        def _get_storage_mock(storage):
            return {
                'splits': storage_mock,
                'segments': mocker.Mock(spec=SegmentStorage),
                'impressions': mocker.Mock(spec=ImpressionStorage),
                'events': mocker.Mock(spec=EventStorage),
                'telemetry': mocker.Mock(spec=TelemetryStorage)
            }[storage]
        factory_mock = mocker.Mock(spec=SplitFactory)
        factory_mock._get_storage.side_effect = _get_storage_mock
        factory_destroyed = mocker.PropertyMock()
        factory_destroyed.return_value = False
        type(factory_mock).destroyed = factory_destroyed

        client = Client(factory_mock)
        client._logger = mocker.Mock()
        mocker.patch('splitio.client.input_validator._LOGGER', new=client._logger)

        assert client.get_treatment_with_config(None, 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed a null key, key must be a non-empty string.', 'get_treatment_with_config')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config('', 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an empty %s, %s must be a non-empty string.', 'get_treatment_with_config', 'key', 'key')
        ]

        client._logger.reset_mock()
        key = ''.join('a' for _ in range(0, 255))
        assert client.get_treatment_with_config(key, 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: %s too long - must be %s characters or less.', 'get_treatment_with_config', 'key', 250)
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(12345, 'some_feature') == ('default_treatment', '{"some": "property"}')
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: %s %s is not of type string, converting.', 'get_treatment_with_config', 'key', 12345)
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(float('nan'), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(float('inf'), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(True, 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config([], 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config('some_key', None) == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed a null %s, %s must be a non-empty string.', 'get_treatment_with_config', 'feature_name', 'feature_name')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config('some_key', 123) == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'feature_name', 'feature_name')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config('some_key', True) == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'feature_name', 'feature_name')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config('some_key', []) == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'feature_name', 'feature_name')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config('some_key', '') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an empty %s, %s must be a non-empty string.', 'get_treatment_with_config', 'feature_name', 'feature_name')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config('some_key', 'some_feature') == ('default_treatment', '{"some": "property"}')
        assert client._logger.error.mock_calls == []
        assert client._logger.warning.mock_calls == []

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key(None, 'bucketing_key'), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed a null %s, %s must be a non-empty string.', 'get_treatment_with_config', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key('', 'bucketing_key'), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an empty %s, %s must be a non-empty string.', 'get_treatment_with_config', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key(float('nan'), 'bucketing_key'), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key(float('inf'), 'bucketing_key'), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key(True, 'bucketing_key'), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key([], 'bucketing_key'), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'matching_key', 'matching_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key(12345, 'bucketing_key'), 'some_feature') == ('default_treatment', '{"some": "property"}')
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: %s %s is not of type string, converting.', 'get_treatment_with_config', 'matching_key', 12345)
        ]

        client._logger.reset_mock()
        key = ''.join('a' for _ in range(0, 255))
        assert client.get_treatment_with_config(Key(key, 'bucketing_key'), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: %s too long - must be %s characters or less.', 'get_treatment_with_config', 'matching_key', 250)
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key('mathcing_key', None), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed a null %s, %s must be a non-empty string.', 'get_treatment_with_config', 'bucketing_key', 'bucketing_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key('mathcing_key', True), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'bucketing_key', 'bucketing_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key('mathcing_key', []), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatment_with_config', 'bucketing_key', 'bucketing_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key('mathcing_key', ''), 'some_feature') == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an empty %s, %s must be a non-empty string.', 'get_treatment_with_config', 'bucketing_key', 'bucketing_key')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config(Key('mathcing_key', 12345), 'some_feature') == ('default_treatment', '{"some": "property"}')
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: %s %s is not of type string, converting.', 'get_treatment_with_config', 'bucketing_key', 12345)
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config('mathcing_key', 'some_feature', True) == (CONTROL, None)
        assert client._logger.error.mock_calls == [
            mocker.call('%s: attributes must be of type dictionary.', 'get_treatment_with_config')
        ]

        client._logger.reset_mock()
        assert client.get_treatment_with_config('mathcing_key', 'some_feature', {'test': 'test'}) == ('default_treatment', '{"some": "property"}')
        assert client._logger.error.mock_calls == []

        client._logger.reset_mock()
        assert client.get_treatment_with_config('mathcing_key', 'some_feature', None) == ('default_treatment', '{"some": "property"}')
        assert client._logger.error.mock_calls == []

        client._logger.reset_mock()
        assert client.get_treatment_with_config('mathcing_key', '  some_feature   ', None) == ('default_treatment', '{"some": "property"}')
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: feature_name \'%s\' has extra whitespace, trimming.', 'get_treatment_with_config', '  some_feature   ')
        ]

    def test_track(self, mocker):
        """Test track method()."""
        events_storage_mock = mocker.Mock(spec=EventStorage)
        events_storage_mock.put.return_value = True
        factory_mock = mocker.Mock(spec=SplitFactory)
        factory_destroyed = mocker.PropertyMock()
        factory_destroyed.return_value = False
        type(factory_mock).destroyed = factory_destroyed

        client = Client(factory_mock)
        client._events_storage = mocker.Mock(spec=EventStorage)
        client._events_storage.put.return_value = True
        client._logger = mocker.Mock()
        mocker.patch('splitio.client.input_validator._LOGGER', new=client._logger)

        assert client.track(None, "traffic_type", "event_type", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed a null %s, %s must be a non-empty string.", 'track', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.track("", "traffic_type", "event_type", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed an empty %s, %s must be a non-empty string.", 'track', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.track(12345, "traffic_type", "event_type", 1) is True
        assert client._logger.warning.mock_calls == [
            mocker.call("%s: %s %s is not of type string, converting.", 'track', 'key', 12345)
        ]

        client._logger.reset_mock()
        assert client.track(True, "traffic_type", "event_type", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed an invalid %s, %s must be a non-empty string.", 'track', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.track([], "traffic_type", "event_type", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed an invalid %s, %s must be a non-empty string.", 'track', 'key', 'key')
        ]

        client._logger.reset_mock()
        key = ''.join('a' for _ in range(0, 255))
        assert client.track(key, "traffic_type", "event_type", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: %s too long - must be %s characters or less.", 'track', 'key', 250)
        ]

        client._logger.reset_mock()
        assert client.track("some_key", None, "event_type", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed a null %s, %s must be a non-empty string.", 'track', 'traffic_type', 'traffic_type')
        ]

        client._logger.reset_mock()
        assert client.track("some_key", "", "event_type", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed an empty %s, %s must be a non-empty string.", 'track', 'traffic_type', 'traffic_type')
        ]

        client._logger.reset_mock()
        assert client.track("some_key", 12345, "event_type", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed an invalid %s, %s must be a non-empty string.", 'track', 'traffic_type', 'traffic_type')
        ]

        client._logger.reset_mock()
        assert client.track("some_key", True, "event_type", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed an invalid %s, %s must be a non-empty string.", 'track', 'traffic_type', 'traffic_type')
        ]

        client._logger.reset_mock()
        assert client.track("some_key", [], "event_type", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed an invalid %s, %s must be a non-empty string.", 'track', 'traffic_type', 'traffic_type')
        ]

        client._logger.reset_mock()
        assert client.track("some_key", "TRAFFIC_type", "event_type", 1) is True
        assert client._logger.warning.mock_calls == [
            mocker.call("track: %s should be all lowercase - converting string to lowercase.", 'TRAFFIC_type')
        ]

        assert client.track("some_key", "traffic_type", None, 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed a null %s, %s must be a non-empty string.", 'track', 'event_type', 'event_type')
        ]

        client._logger.reset_mock()
        assert client.track("some_key", "traffic_type", "", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed an empty %s, %s must be a non-empty string.", 'track', 'event_type', 'event_type')
        ]

        client._logger.reset_mock()
        assert client.track("some_key", "traffic_type", True, 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed an invalid %s, %s must be a non-empty string.", 'track', 'event_type', 'event_type')
        ]

        client._logger.reset_mock()
        assert client.track("some_key", "traffic_type", [], 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed an invalid %s, %s must be a non-empty string.", 'track', 'event_type', 'event_type')
        ]

        client._logger.reset_mock()
        assert client.track("some_key", "traffic_type", 12345, 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed an invalid %s, %s must be a non-empty string.", 'track', 'event_type', 'event_type')
        ]

        client._logger.reset_mock()
        assert client.track("some_key", "traffic_type", "@@", 1) is False
        assert client._logger.error.mock_calls == [
            mocker.call("%s: you passed %s, event_type must adhere to the regular "
                        "expression %s. This means "
                        "an event name must be alphanumeric, cannot be more than 80 "
                        "characters long, and can only include a dash, underscore, "
                        "period, or colon as separators of alphanumeric characters.",
                        'track', '@@', '^[a-zA-Z0-9][-_.:a-zA-Z0-9]{0,79}$')
        ]

        client._logger.reset_mock()
        assert client.track("some_key", "traffic_type", "event_type", None) is True
        assert client._logger.error.mock_calls == []

        client._logger.reset_mock()
        assert client.track("some_key", "traffic_type", "event_type", 1) is True
        assert client._logger.error.mock_calls == []

        client._logger.reset_mock()
        assert client.track("some_key", "traffic_type", "event_type", 1.23) is True
        assert client._logger.error.mock_calls == []

        client._logger.reset_mock()
        assert client.track("some_key", "traffic_type", "event_type", "test") is False
        assert client._logger.error.mock_calls == [
            mocker.call("track: value must be a number.")
        ]

        client._logger.reset_mock()
        assert client.track("some_key", "traffic_type", "event_type", True) is False
        assert client._logger.error.mock_calls == [
            mocker.call("track: value must be a number.")
        ]

        client._logger.reset_mock()
        assert client.track("some_key", "traffic_type", "event_type", []) is False
        assert client._logger.error.mock_calls == [
            mocker.call("track: value must be a number.")
        ]

    def test_get_treatments(self, mocker):
        """Test getTreatments() method."""
        split_mock = mocker.Mock(spec=Split)
        default_treatment_mock = mocker.PropertyMock()
        default_treatment_mock.return_value = 'default_treatment'
        type(split_mock).default_treatment = default_treatment_mock
        conditions_mock = mocker.PropertyMock()
        conditions_mock.return_value = []
        type(split_mock).conditions = conditions_mock

        storage_mock = mocker.Mock(spec=SplitStorage)
        storage_mock.get.return_value = split_mock

        factory_mock = mocker.Mock(spec=SplitFactory)
        factory_mock._get_storage.return_value = storage_mock
        factory_destroyed = mocker.PropertyMock()
        factory_destroyed.return_value = False
        type(factory_mock).destroyed = factory_destroyed

        client = Client(factory_mock)
        client._logger = mocker.Mock()
        mocker.patch('splitio.client.input_validator._LOGGER', new=client._logger)

        assert client.get_treatments(None, ['some_feature']) == {'some_feature': CONTROL}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed a null key, key must be a non-empty string.', 'get_treatments')
        ]

        client._logger.reset_mock()
        assert client.get_treatments("", ['some_feature']) == {'some_feature': CONTROL}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an empty %s, %s must be a non-empty string.', 'get_treatments', 'key', 'key')
        ]

        key = ''.join('a' for _ in range(0, 255))
        client._logger.reset_mock()
        assert client.get_treatments(key, ['some_feature']) == {'some_feature': CONTROL}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: %s too long - must be %s characters or less.', 'get_treatments', 'key', 250)
        ]

        client._logger.reset_mock()
        assert client.get_treatments(12345, ['some_feature']) == {'some_feature': 'default_treatment'}
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: %s %s is not of type string, converting.', 'get_treatments', 'key', 12345)
        ]

        client._logger.reset_mock()
        assert client.get_treatments(True, ['some_feature']) == {'some_feature': CONTROL}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatments', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatments([], ['some_feature']) == {'some_feature': CONTROL}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatments', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatments('some_key', None) == {}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments')
        ]

        client._logger.reset_mock()
        assert client.get_treatments('some_key', True) == {}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments')
        ]

        client._logger.reset_mock()
        assert client.get_treatments('some_key', 'some_string') == {}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments')
        ]

        client._logger.reset_mock()
        assert client.get_treatments('some_key', []) == {}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments')
        ]

        client._logger.reset_mock()
        assert client.get_treatments('some_key', [None, None]) == {}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments')
        ]

        client._logger.reset_mock()
        assert client.get_treatments('some_key', [True]) == {}
        assert mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments') in client._logger.error.mock_calls

        client._logger.reset_mock()
        assert client.get_treatments('some_key', ['', '']) == {}
        assert mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments') in client._logger.error.mock_calls

        client._logger.reset_mock()
        assert client.get_treatments('some_key', ['some   ']) == {'some': 'default_treatment'}
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: feature_name \'%s\' has extra whitespace, trimming.', 'get_treatments', 'some   ')
        ]

    def test_get_treatments_with_config(self, mocker):
        """Test getTreatments() method."""
        split_mock = mocker.Mock(spec=Split)
        default_treatment_mock = mocker.PropertyMock()
        default_treatment_mock.return_value = 'default_treatment'
        type(split_mock).default_treatment = default_treatment_mock
        conditions_mock = mocker.PropertyMock()
        conditions_mock.return_value = []
        type(split_mock).conditions = conditions_mock

        storage_mock = mocker.Mock(spec=SplitStorage)
        storage_mock.get.return_value = split_mock

        factory_mock = mocker.Mock(spec=SplitFactory)
        factory_mock._get_storage.return_value = storage_mock
        factory_destroyed = mocker.PropertyMock()
        factory_destroyed.return_value = False
        type(factory_mock).destroyed = factory_destroyed
        def _configs(treatment):
            return '{"some": "property"}' if treatment == 'default_treatment' else None
        split_mock.get_configurations_for.side_effect = _configs

        client = Client(factory_mock)
        client._logger = mocker.Mock()
        mocker.patch('splitio.client.input_validator._LOGGER', new=client._logger)

        assert client.get_treatments_with_config(None, ['some_feature']) == {'some_feature': (CONTROL, None)}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed a null key, key must be a non-empty string.', 'get_treatments_with_config')
        ]

        client._logger.reset_mock()
        assert client.get_treatments_with_config("", ['some_feature']) == {'some_feature': (CONTROL, None)}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an empty %s, %s must be a non-empty string.', 'get_treatments_with_config', 'key', 'key')
        ]

        key = ''.join('a' for _ in range(0, 255))
        client._logger.reset_mock()
        assert client.get_treatments_with_config(key, ['some_feature']) == {'some_feature': (CONTROL, None)}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: %s too long - must be %s characters or less.', 'get_treatments_with_config', 'key', 250)
        ]

        client._logger.reset_mock()
        assert client.get_treatments_with_config(12345, ['some_feature']) == {'some_feature': ('default_treatment', '{"some": "property"}')}
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: %s %s is not of type string, converting.', 'get_treatments_with_config', 'key', 12345)
        ]

        client._logger.reset_mock()
        assert client.get_treatments_with_config(True, ['some_feature']) == {'some_feature': (CONTROL, None)}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatments_with_config', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatments_with_config([], ['some_feature']) == {'some_feature': (CONTROL, None)}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: you passed an invalid %s, %s must be a non-empty string.', 'get_treatments_with_config', 'key', 'key')
        ]

        client._logger.reset_mock()
        assert client.get_treatments_with_config('some_key', None) == {}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments_with_config')
        ]

        client._logger.reset_mock()
        assert client.get_treatments_with_config('some_key', True) == {}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments_with_config')
        ]

        client._logger.reset_mock()
        assert client.get_treatments_with_config('some_key', 'some_string') == {}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments_with_config')
        ]

        client._logger.reset_mock()
        assert client.get_treatments_with_config('some_key', []) == {}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments_with_config')
        ]

        client._logger.reset_mock()
        assert client.get_treatments_with_config('some_key', [None, None]) == {}
        assert client._logger.error.mock_calls == [
            mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments_with_config')
        ]

        client._logger.reset_mock()
        assert client.get_treatments_with_config('some_key', [True]) == {}
        assert mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments_with_config') in client._logger.error.mock_calls

        client._logger.reset_mock()
        assert client.get_treatments_with_config('some_key', ['', '']) == {}
        assert mocker.call('%s: feature_names must be a non-empty array.', 'get_treatments_with_config') in client._logger.error.mock_calls

        client._logger.reset_mock()
        assert client.get_treatments_with_config('some_key', ['some_feature   ']) == {'some_feature': ('default_treatment', '{"some": "property"}')}
        assert client._logger.warning.mock_calls == [
            mocker.call('%s: feature_name \'%s\' has extra whitespace, trimming.', 'get_treatments_with_config', 'some_feature   ')
        ]


class ManagerInputValidationTests(object):  #pylint: disable=too-few-public-methods
    """Manager input validation test cases."""

    def test_split_(self, mocker):
        """Test split input validation."""
        storage_mock = mocker.Mock(spec=SplitStorage)
        split_mock = mocker.Mock(spec=Split)
        storage_mock.get.return_value = split_mock
        factory_mock = mocker.Mock(spec=SplitFactory)
        factory_mock._get_storage.return_value = storage_mock
        factory_destroyed = mocker.PropertyMock()
        factory_destroyed.return_value = False
        type(factory_mock).destroyed = factory_destroyed

        manager = SplitManager(factory_mock)
        manager._logger = mocker.Mock()
        mocker.patch('splitio.client.input_validator._LOGGER', new=manager._logger)

        assert manager.split(None) is None
        assert manager._logger.error.mock_calls == [
            mocker.call("%s: you passed a null %s, %s must be a non-empty string.", 'split', 'feature_name', 'feature_name')
        ]

        manager._logger.reset_mock()
        assert manager.split("") is None
        assert manager._logger.error.mock_calls == [
            mocker.call("%s: you passed an empty %s, %s must be a non-empty string.", 'split', 'feature_name', 'feature_name')
        ]

        manager._logger.reset_mock()
        assert manager.split(True) is None
        assert manager._logger.error.mock_calls == [
            mocker.call("%s: you passed an invalid %s, %s must be a non-empty string.", 'split', 'feature_name', 'feature_name')
        ]

        manager._logger.reset_mock()
        assert manager.split([]) is None
        assert manager._logger.error.mock_calls == [
            mocker.call("%s: you passed an invalid %s, %s must be a non-empty string.", 'split', 'feature_name', 'feature_name')
        ]

        manager._logger.reset_mock()
        manager.split('some_split')
        assert split_mock.to_split_view.mock_calls == [mocker.call()]
        assert manager._logger.error.mock_calls == []


class FactoryInputValidationTests(object):  #pylint: disable=too-few-public-methods
    """Factory instantiation input validation test cases."""

    def test_input_validation_factory(self, mocker):
        """Test the input validators for factory instantiation."""
        logger = mocker.Mock(spec=logging.Logger)
        mocker.patch('splitio.client.input_validator._LOGGER', new=logger)

        assert get_factory(None) is None
        assert logger.error.mock_calls == [
            mocker.call("%s: you passed a null %s, %s must be a non-empty string.", 'factory_instantiation', 'apikey', 'apikey')
        ]

        logger.reset_mock()
        assert get_factory('') is None
        assert logger.error.mock_calls == [
            mocker.call("%s: you passed an empty %s, %s must be a non-empty string.", 'factory_instantiation', 'apikey', 'apikey')
        ]

        logger.reset_mock()
        assert get_factory(True) is None
        assert logger.error.mock_calls == [
            mocker.call("%s: you passed an invalid %s, %s must be a non-empty string.", 'factory_instantiation', 'apikey', 'apikey')
        ]

        logger.reset_mock()
        assert get_factory(True, config={'uwsgiClient': True}) is not None
        assert logger.error.mock_calls == []

        logger.reset_mock()
        assert get_factory(True, config={'redisHost': 'some-host'}) is not None
        assert logger.error.mock_calls == []
