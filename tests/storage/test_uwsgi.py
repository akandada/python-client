"""UWSGI Storage unit tests."""
#pylint: disable=no-self-usage
import json

from splitio.storage.uwsgi import UWSGIEventStorage, UWSGIImpressionStorage,  \
    UWSGISegmentStorage, UWSGISplitStorage,  UWSGITelemetryStorage

from splitio.models.splits import Split
from splitio.models.segments import Segment
from splitio.models.impressions import Impression
from splitio.models.events import Event

from splitio.storage.adapters.uwsgi_cache import get_uwsgi


class UWSGISplitStorageTests(object):
    """UWSGI Split Storage test cases."""

    def test_store_retrieve_split(self, mocker):
        """Test storing and retrieving splits."""
        uwsgi = get_uwsgi(True)
        storage = UWSGISplitStorage(uwsgi)
        split = mocker.Mock(spec=Split)
        split.to_json.return_value = '{}'
        split_name = mocker.PropertyMock()
        split_name.return_value = 'some_split'
        type(split).name = split_name
        storage.put(split)

        from_raw_mock = mocker.Mock()
        from_raw_mock.return_value = 'ok'
        mocker.patch('splitio.models.splits.from_raw', new=from_raw_mock)
        retrieved = storage.get('some_split')

        assert retrieved == 'ok'
        assert from_raw_mock.mock_calls == [mocker.call('{}')]
        assert split.to_json.mock_calls == [mocker.call()]

        assert storage.get('nonexistant_split') is None

        storage.remove('some_split')
        assert storage.get('some_split') == None

    def test_set_get_changenumber(self, mocker):
        """Test setting and retrieving changenumber."""
        uwsgi = get_uwsgi(True)
        storage = UWSGISplitStorage(uwsgi)

        assert storage.get_change_number() == None
        storage.set_change_number(123)
        assert storage.get_change_number() == 123

    def test_get_split_names(self, mocker):
        """Test getting all split names."""
        uwsgi = get_uwsgi(True)
        storage = UWSGISplitStorage(uwsgi)
        split_1 = mocker.Mock(spec=Split)
        split_1.to_json.return_value = '{"name": "split1"}'
        split_name_1 = mocker.PropertyMock()
        split_name_1.return_value = 'some_split_1'
        type(split_1).name = split_name_1
        split_2 = mocker.Mock(spec=Split)
        split_2.to_json.return_value = '{"name": "split2"}'
        split_name_2 = mocker.PropertyMock()
        split_name_2.return_value = 'some_split_2'
        type(split_2).name = split_name_2
        storage.put(split_1)
        storage.put(split_2)
        assert set(storage.get_split_names()) == set(['some_split_1', 'some_split_2'])
        storage.remove('some_split_1')
        assert storage.get_split_names() == ['some_split_2']

    def test_get_all_splits(self, mocker):
        """Test fetching all splits."""
        uwsgi = get_uwsgi(True)
        storage = UWSGISplitStorage(uwsgi)
        split_1 = mocker.Mock(spec=Split)
        split_1.to_json.return_value = '{"name": "some_split_1"}'
        split_name_1 = mocker.PropertyMock()
        split_name_1.return_value = 'some_split_1'
        type(split_1).name = split_name_1
        split_2 = mocker.Mock(spec=Split)
        split_2.to_json.return_value = '{"name": "some_split_2"}'
        split_name_2 = mocker.PropertyMock()
        split_name_2.return_value = 'some_split_2'
        type(split_2).name = split_name_2

        def _from_raw_mock(split_json):
            split_mock = mocker.Mock(spec=Split)
            name = mocker.PropertyMock()
            name.return_value = json.loads(split_json)['name']
            type(split_mock).name = name
            return split_mock
        mocker.patch('splitio.storage.uwsgi.splits.from_raw', new=_from_raw_mock)

        storage.put(split_1)
        storage.put(split_2)

        splits = storage.get_all_splits()
        s1 = next(split for split in splits if split.name == 'some_split_1')
        s2 = next(split for split in splits if split.name == 'some_split_2')



class UWSGISegmentStorageTests(object):
    """UWSGI Segment storage test cases."""

    def test_store_retrieve_segment(self, mocker):
        """Test storing and fetching segments."""
        uwsgi = get_uwsgi(True)
        storage = UWSGISegmentStorage(uwsgi)
        segment = mocker.Mock(spec=Segment)
        segment_keys = mocker.PropertyMock()
        segment_keys.return_value = ['abc']
        type(segment).keys = segment_keys
        segment.to_json = {}
        segment_name = mocker.PropertyMock()
        segment_name.return_value = 'some_segment'
        segment_change_number = mocker.PropertyMock()
        segment_change_number.return_value = 123
        type(segment).name = segment_name
        type(segment).change_number = segment_change_number
        from_raw_mock = mocker.Mock()
        from_raw_mock.return_value = 'ok'
        mocker.patch('splitio.models.segments.from_raw', new=from_raw_mock)

        storage.put(segment)
        assert storage.get('some_segment') == 'ok'
        assert from_raw_mock.mock_calls == [mocker.call({'till': 123, 'removed': [], 'added': [u'abc'], 'name': 'some_segment'})]
        assert storage.get('nonexistant-segment') is None

    def test_get_set_change_number(self, mocker):
        """Test setting and getting change number."""
        uwsgi = get_uwsgi(True)
        storage = UWSGISegmentStorage(uwsgi)
        assert storage.get_change_number('some_segment') is None
        storage.set_change_number('some_segment', 123)
        assert storage.get_change_number('some_segment') == 123

    def test_segment_contains(self, mocker):
        """Test that segment contains works properly."""
        uwsgi = get_uwsgi(True)
        storage = UWSGISegmentStorage(uwsgi)

        from_raw_mock = mocker.Mock()
        from_raw_mock.return_value = Segment('some_segment', ['abc'], 123)
        mocker.patch('splitio.models.segments.from_raw', new=from_raw_mock)
        segment = mocker.Mock(spec=Segment)
        segment_keys = mocker.PropertyMock()
        segment_keys.return_value = ['abc']
        type(segment).keys = segment_keys
        segment.to_json = {}
        segment_name = mocker.PropertyMock()
        segment_name.return_value = 'some_segment'
        segment_change_number = mocker.PropertyMock()
        segment_change_number.return_value = 123
        type(segment).name = segment_name
        type(segment).change_number = segment_change_number
        storage.put(segment)

        assert storage.segment_contains('some_segment', 'abc')
        assert not storage.segment_contains('some_segment', 'qwe')



class UWSGIImpressionsStorageTests(object):
    """UWSGI Impressions storage test cases."""

    def test_put_pop_impressions(self, mocker):
        """Test storing and fetching impressions."""
        uwsgi = get_uwsgi(True)
        storage = UWSGIImpressionStorage(uwsgi)
        impressions = [
            Impression('key1', 'feature1', 'on', 'some_label', 123456, 'buck1', 321654),
            Impression('key2', 'feature2', 'on', 'some_label', 123456, 'buck1', 321654),
            Impression('key3', 'feature2', 'on', 'some_label', 123456, 'buck1', 321654),
            Impression('key4', 'feature1', 'on', 'some_label', 123456, 'buck1', 321654)
        ]
        storage.put(impressions)
        res = storage.pop_many(10)
        assert res == impressions

    def test_flush(self):
        """Test requesting, querying and acknowledging a flush."""
        uwsgi = get_uwsgi(True)
        storage = UWSGIImpressionStorage(uwsgi)
        assert storage.should_flush() is False
        storage.request_flush()
        assert storage.should_flush() is True
        storage.acknowledge_flush()
        assert storage.should_flush() is False




class UWSGIEventsStorageTests(object):
    """UWSGI Events storage test cases."""

    def test_put_pop_events(self, mocker):
        """Test storing and fetching events."""
        uwsgi = get_uwsgi(True)
        storage = UWSGIEventStorage(uwsgi)
        events = [
            Event('key1', 'user', 'purchase', 10, 123456),
            Event('key2', 'user', 'purchase', 10, 123456),
            Event('key3', 'user', 'purchase', 10, 123456),
            Event('key4', 'user', 'purchase', 10, 123456),
        ]

        storage.put(events)
        res = storage.pop_many(10)
        assert res == events

class UWSGITelemetryStorageTests(object):
    """UWSGI-based telemetry storage test cases."""

    def test_latencies(self):
        """Test storing and popping latencies."""
        storage = UWSGITelemetryStorage(get_uwsgi(True))
        storage.inc_latency('some_latency', 2)
        storage.inc_latency('some_latency', 2)
        storage.inc_latency('some_latency', 2)
        assert storage.pop_latencies() == {
            'some_latency': [0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        assert storage.pop_latencies() == {}

    def test_counters(self):
        """Test storing and popping counters."""
        storage = UWSGITelemetryStorage(get_uwsgi(True))
        storage.inc_counter('some_counter')
        storage.inc_counter('some_counter')
        storage.inc_counter('some_counter')
        assert storage.pop_counters() == {'some_counter': 3}
        assert storage.pop_counters() == {}

    def test_gauges(self):
        """Test storing and popping gauges."""
        storage = UWSGITelemetryStorage(get_uwsgi(True))
        storage.put_gauge('some_gauge1', 123)
        storage.put_gauge('some_gauge2', 456)
        assert storage.pop_gauges() == {'some_gauge1': 123, 'some_gauge2': 456}
        assert storage.pop_gauges() == {}

