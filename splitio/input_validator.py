from __future__ import absolute_import, division, print_function, \
    unicode_literals

from numbers import Number
import logging
import six
import re
import math
from splitio.key import Key

_LOGGER = logging.getLogger(__name__)


def _check_not_null(value, name, operation):
    """
    Checks if value is null

    :param key: value to be checked
    :type key: str
    :param name: name to inform the error
    :type feature: str
    :param operation: operation to inform the error
    :type operation: str
    :return: The result of validation
    :rtype: True|False
    """
    if value is None:
        _LOGGER.error('{}: you passed a null {}, {} must be a non-empty string.'
                      .format(operation, name, name))
        return False
    return True


def _check_is_string(value, name, operation):
    """
    Checks if value is not string

    :param key: value to be checked
    :type key: str
    :param name: name to inform the error
    :type feature: str
    :param operation: operation to inform the error
    :type operation: str
    :return: The result of validation
    :rtype: True|False
    """
    if isinstance(value, six.string_types) is False:
        _LOGGER.error('{}: you passed an invalid {}, {} must be a non-empty string.'.format(
                      operation, name, name))
        return False
    return True


def _check_string_not_empty(value, name, operation):
    """
    Checks if value is an empty string

    :param key: value to be checked
    :type key: str
    :param name: name to inform the error
    :type feature: str
    :param operation: operation to inform the error
    :type operation: str
    :return: The result of validation
    :rtype: True|False
    """
    if value.strip() == "":
        _LOGGER.error('{}: you passed an empty {}, {} must be a non-empty string.'
                      .format(operation, name, name))
        return False
    return True


def _check_string_matches(value, operation, pattern):
    """
    Checks if value is adhere to a regular expression passed

    :param key: value to be checked
    :type key: str
    :param operation: operation to inform the error
    :type operation: str
    :param pattern: pattern that needs to adhere
    :type pattern: str
    :return: The result of validation
    :rtype: True|False
    """
    if not re.match(pattern, value):
        _LOGGER.error('{}: you passed {}, event_type must '.format(operation, value) +
                      'adhere to the regular expression {}. '.format(pattern) +
                      'This means an event name must be alphanumeric, cannot be more ' +
                      'than 80 characters long, and can only include a dash, underscore, ' +
                      'period, or colon as separators of alphanumeric characters.'
                      )
        return False
    return True


def _check_can_convert(value, name, operation):
    """
    Checks if is a valid convertion.

    :param key: value to be checked
    :type key: bool|number|array|
    :param name: name to inform the error
    :type feature: str
    :param operation: operation to inform the error
    :type operation: str
    :return: The result of validation
    :rtype: True|False
    """
    if isinstance(value, six.string_types):
        return True
    else:
        if isinstance(value, bool) or (not isinstance(value, Number)) or math.isnan(value) \
           or math.isinf(value):
            _LOGGER.error('{}: you passed an invalid {}, {} must be a non-empty string.'
                          .format(operation, name, name))
            return False
    _LOGGER.warning('{}: {} {} is not of type string, converting.'
                    .format(operation, name, value))
    return True


def _check_valid_length(value, name, operation):
    """
    Checks value's length

    :param key: value to be checked
    :type key: str
    :param name: name to inform the error
    :type feature: str
    :param operation: operation to inform the error
    :type operation: str
    :return: The result of validation
    :rtype: True|False
    """
    if len(value) > 250:
        _LOGGER.error('{}: {} too long - must be 250 characters or less.'
                      .format(operation, name))
        return False
    return True


def _check_valid_matching_key(matching_key, operation):
    """
    Checks if matching_key is valid for get_treatment when is
    sent as Key Object

    :param matching_key: matching_key to be checked
    :type matching_key: str
    :param operation: user operation
    :type operation: str
    :return: The result of validation
    :rtype: str|None
    """
    if matching_key is None:
        _LOGGER.error('{}: you passed a null matching_key, matching_key '.format(operation)
                      + 'must be a non-empty string.')
        return None
    if isinstance(matching_key, six.string_types):
        if not _check_string_not_empty(matching_key, 'matching_key', operation):
            return None
    else:
        if not _check_can_convert(matching_key, 'matching_key', operation):
            return None
    matching_key = str(matching_key)
    if _check_valid_length(matching_key, 'matching_key', operation):
        return matching_key
    return None


def _check_valid_bucketing_key(bucketing_key, operation):
    """
    Checks if bucketing_key is valid for get_treatment when is
    sent as Key Object

    :param bucketing_key: bucketing_key to be checked
    :type bucketing_key: str
    :param operation: user operation
    :type operation: str
    :return: The result of validation
    :rtype: str|None
    """
    if bucketing_key is None:
        _LOGGER.error('{}: you passed a null bucketing_key, '.format(operation)
                      + 'bucketing_key must be a non-empty string.')
        return None
    if isinstance(bucketing_key, six.string_types):
        if not _check_string_not_empty(bucketing_key, 'bucketing_key', operation):
            return None
    else:
        if not _check_can_convert(bucketing_key, 'bucketing_key', operation):
            return None
    bucketing_key = str(bucketing_key)
    if _check_valid_length(bucketing_key, 'bucketing_key', operation):
        return bucketing_key
    return None


def _remove_empty_spaces(value, operation):
    """
    Checks if an string has whitespaces

    :param value: value to be checked
    :type value: str
    :param operation: user operation
    :type operation: str
    :return: The result of trimming
    :rtype: str
    """
    strip_value = value.strip()
    if len(value) != len(strip_value):
        _LOGGER.warning("{}: feature_name '{}' has extra whitespace,".format(operation, value)
                        + " trimming.")
    return strip_value


def validate_key(key, operation):
    """
    Validate Key parameter for get_treatment, if is invalid at some point
    the bucketing_key or matching_key it will return None

    :param key: user key
    :type key: mixed
    :param operation: user operation
    :type operation: str
    :return: The tuple key
    :rtype: (matching_key,bucketing_key)
    """
    matching_key_result = None
    bucketing_key_result = None
    if key is None:
        _LOGGER.error('{}: you passed a null key, key must be a non-empty string.'
                      .format(operation))
        return None, None

    if isinstance(key, Key):
        matching_key_result = _check_valid_matching_key(key.matching_key, operation)
        if matching_key_result is None:
            return None, None
        bucketing_key_result = _check_valid_bucketing_key(key.bucketing_key, operation)
        if bucketing_key_result is None:
            return None, None
    else:
        if _check_can_convert(key, 'key', operation) and \
           _check_string_not_empty(str(key), 'key', operation) and \
           _check_valid_length(str(key), 'key', operation):
            matching_key_result = str(key)
    return matching_key_result, bucketing_key_result


def validate_feature_name(feature_name):
    """
    Checks if feature_name is valid for get_treatment

    :param feature_name: feature_name to be checked
    :type feature_name: str
    :return: feature_name
    :rtype: str|None
    """
    if (not _check_not_null(feature_name, 'feature_name', 'get_treatment')) or \
       (not _check_is_string(feature_name, 'feature_name', 'get_treatment')) or \
       (not _check_string_not_empty(feature_name, 'feature_name', 'get_treatment')):
        return None
    return _remove_empty_spaces(feature_name, 'get_treatment')


def validate_track_key(key):
    """
    Checks if key is valid for track

    :param key: key to be checked
    :type key: str
    :return: key
    :rtype: str|None
    """
    if (not _check_not_null(key, 'key', 'track')) or \
       (not _check_can_convert(key, 'key', 'track')) or \
       (not _check_string_not_empty(str(key), 'key', 'track')) or \
       (not _check_valid_length(str(key), 'key', 'track')):
        return None
    return str(key)


def validate_traffic_type(traffic_type):
    """
    Checks if traffic_type is valid for track

    :param traffic_type: traffic_type to be checked
    :type traffic_type: str
    :return: traffic_type
    :rtype: str|None
    """
    if (not _check_not_null(traffic_type, 'traffic_type', 'track')) or \
       (not _check_is_string(traffic_type, 'traffic_type', 'track')) or \
       (not _check_string_not_empty(traffic_type, 'traffic_type', 'track')):
        return None
    if not traffic_type.islower():
        _LOGGER.warning('track: {} should be all lowercase - converting string to lowercase.'
                        .format(traffic_type))
        traffic_type = traffic_type.lower()
    return traffic_type


def validate_event_type(event_type):
    """
    Checks if event_type is valid for track

    :param event_type: event_type to be checked
    :type event_type: str
    :return: event_type
    :rtype: str|None
    """
    if (not _check_not_null(event_type, 'event_type', 'track')) or \
       (not _check_is_string(event_type, 'event_type', 'track')) or \
       (not _check_string_not_empty(event_type, 'event_type', 'track')) or \
       (not _check_string_matches(event_type, 'track',
                                  r'^[a-zA-Z0-9][-_.:a-zA-Z0-9]{0,79}$')):
        return None
    return event_type


def validate_value(value):
    """
    Checks if value is valid for track

    :param value: value to be checked
    :type value: number
    :return: value
    :rtype: number|None
    """
    if value is None:
        return None
    if (not isinstance(value, Number)) or isinstance(value, bool):
        _LOGGER.error('track: value must be a number.')
        return False
    return value


def validate_manager_feature_name(feature_name):
    """
    Checks if feature_name is valid for track

    :param feature_name: feature_name to be checked
    :type feature_name: str
    :return: feature_name
    :rtype: str|None
    """
    if (not _check_not_null(feature_name, 'feature_name', 'split')) or \
       (not _check_is_string(feature_name, 'feature_name', 'split')) or \
       (not _check_string_not_empty(feature_name, 'feature_name', 'split')):
        return None
    return feature_name


def validate_features_get_treatments(features):
    """
    Checks if features is valid for get_treatments

    :param features: array of features
    :type features: list
    :return: filtered_features
    :rtype: list|None
    """
    if features is None or not isinstance(features, list):
        _LOGGER.error('get_treatments: feature_names must be a non-empty array.')
        return None
    if len(features) == 0:
        _LOGGER.error('get_treatments: feature_names must be a non-empty array.')
        return []
    filtered_features = set(_remove_empty_spaces(feature, 'get_treatments') for feature in features
                            if feature is not None and
                            _check_is_string(feature, 'feature_name', 'get_treatments') and
                            _check_string_not_empty(feature, 'feature_name', 'get_treatments')
                            )
    if len(filtered_features) == 0:
        _LOGGER.error('get_treatments: feature_names must be a non-empty array.')
        return None
    return filtered_features


def validate_attributes(attributes, operation):
    """
    Checks if attributes is valid

    :param attributes: dict
    :type attributes: dict
    :param operation: user operation
    :type operation: str
    :return: bool
    :rtype: True|False
    """
    if attributes is None:
        return True
    if not type(attributes) is dict:
        _LOGGER.error('{}: attributes must be of type dictionary.'
                      .format(operation))
        return False
    return True


def validate_factory_instantiation(apikey):
    """
    Checks if is a valid instantiation of split client

    :param apikey: str
    :type apikey: str
    :return: bool
    :rtype: True|False
    """
    if (not _check_not_null(apikey, 'apikey', 'factory_instantiation')) or \
       (not _check_is_string(apikey, 'apikey', 'factory_instantiation')) or \
       (not _check_string_not_empty(apikey, 'apikey', 'factory_instantiation')):
        return False
    return True
