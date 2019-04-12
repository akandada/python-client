"""Asynctask test module."""

import time
import threading
from splitio.tasks.util import asynctask


class AsyncTaskTests(object):
    """AsyncTask test cases."""

    def test_default_task_flow(self, mocker):
        """Test the default execution flow of an asynctask."""
        main_func = mocker.Mock()
        on_init = mocker.Mock()
        on_stop = mocker.Mock()
        on_stop_event = threading.Event()

        task = asynctask.AsyncTask(main_func, 0.5, on_init, on_stop)
        task.start()
        time.sleep(1)
        assert task.running()
        task.stop(on_stop_event)
        on_stop_event.wait()

        assert on_stop_event.is_set()
        assert 0 < len(main_func.mock_calls) <= 2
        assert len(on_init.mock_calls) == 1
        assert len(on_stop.mock_calls) == 1
        assert not task.running()

    def test_main_exception_skips_iteration(self, mocker):
        """Test that an exception in the main func only skips current iteration."""
        def raise_exception():
            raise Exception('something')
        main_func = mocker.Mock()
        main_func.side_effect = raise_exception
        on_init = mocker.Mock()
        on_stop = mocker.Mock()
        on_stop_event = threading.Event()

        task = asynctask.AsyncTask(main_func, 0.1, on_init, on_stop)
        task.start()
        time.sleep(1)
        assert task.running()
        task.stop(on_stop_event)
        on_stop_event.wait()

        assert on_stop_event.is_set()
        assert 9 <= len(main_func.mock_calls) <= 10
        assert len(on_init.mock_calls) == 1
        assert len(on_stop.mock_calls) == 1
        assert not task.running()

    def test_on_init_failure_aborts_task(self, mocker):
        """Test that if the on_init callback fails, the task never runs."""
        def raise_exception():
            raise Exception('something')
        main_func = mocker.Mock()
        on_init = mocker.Mock()
        on_init.side_effect = raise_exception
        on_stop = mocker.Mock()
        on_stop_event = threading.Event()

        task = asynctask.AsyncTask(main_func, 0.1, on_init, on_stop)
        task.start()
        time.sleep(0.5)
        assert not task.running() # Since on_init fails, task never starts
        task.stop(on_stop_event)
        on_stop_event.wait(1)

        assert on_stop_event.is_set()
        assert on_init.mock_calls == [mocker.call()]
        assert on_stop.mock_calls == [mocker.call()]
        assert main_func.mock_calls == []
        assert not task.running()

    def test_on_stop_failure_ends_gacefully(self, mocker):
        """Test that if the on_init callback fails, the task never runs."""
        def raise_exception():
            raise Exception('something')
        main_func = mocker.Mock()
        on_init = mocker.Mock()
        on_stop = mocker.Mock()
        on_stop.side_effect = raise_exception
        on_stop_event = threading.Event()

        task = asynctask.AsyncTask(main_func, 0.1, on_init, on_stop)
        task.start()
        time.sleep(1)
        task.stop(on_stop_event)
        on_stop_event.wait(1)

        assert on_stop_event.isSet()
        assert on_init.mock_calls == [mocker.call()]
        assert on_stop.mock_calls == [mocker.call()]
        assert 9 <= len(main_func.mock_calls) <= 10

    def test_force_run(self, mocker):
        """Test that if the on_init callback fails, the task never runs."""
        main_func = mocker.Mock()
        on_init = mocker.Mock()
        on_stop = mocker.Mock()
        on_stop_event = threading.Event()

        task = asynctask.AsyncTask(main_func, 5, on_init, on_stop)
        task.start()
        time.sleep(1)
        assert task.running()
        task.force_execution()
        task.force_execution()
        task.stop(on_stop_event)
        on_stop_event.wait(1)

        assert on_stop_event.isSet()
        assert on_init.mock_calls == [mocker.call()]
        assert on_stop.mock_calls == [mocker.call()]
        assert len(main_func.mock_calls) == 2
        assert not task.running()
