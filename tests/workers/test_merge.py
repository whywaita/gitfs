import pytest
from mock import patch, MagicMock

from gitfs.worker.merge import MergeWorker


class TestMergeWorker(object):
    def test_run(self):
        mocked_queue = MagicMock()
        mocked_idle = MagicMock(side_effect=ValueError)

        mocked_queue.get.side_effect = ValueError()

        worker = MergeWorker("name", "email", "name", "email",
                             strategy="strategy", merge_queue=mocked_queue)
        worker.on_idle = mocked_idle
        worker.timeout = 1

        with pytest.raises(ValueError):
            worker.run()

        mocked_queue.get.assert_called_once_with(timeout=1, block=True)
        mocked_idle.assert_called_once_with([], [])

    def test_on_idle_with_commits_and_merges(self):
        mocked_want_to_merge = MagicMock()
        mocked_commit = MagicMock()

        worker = MergeWorker("name", "email", "name", "email",
                             strategy="strategy",
                             want_to_merge=mocked_want_to_merge)
        worker.commit = mocked_commit

        commits, merges = worker.on_idle("commits", "merges")

        mocked_commit.assert_called_once_with("commits")
        assert mocked_want_to_merge.set.call_count == 1
        assert commits == []
        assert merges == []

    def test_on_idle_with_merges_and_no_commits(self):
        mocked_want_to_merge = MagicMock()

        worker = MergeWorker("name", "email", "name", "email",
                             strategy="strategy",
                             want_to_merge=mocked_want_to_merge)

        commits, merges = worker.on_idle(None, "merges")

        assert mocked_want_to_merge.set.call_count == 1
        assert commits is None
        assert merges == []

    def test_on_idle_with_commits_and_no_merges(self):
        mocked_want_to_merge = MagicMock()
        mocked_commit = MagicMock()

        worker = MergeWorker("name", "email", "name", "email",
                             strategy="strategy",
                             want_to_merge=mocked_want_to_merge)
        worker.commit = mocked_commit

        commits, merges = worker.on_idle("commits", None)

        mocked_commit.assert_called_once_with("commits")
        assert mocked_want_to_merge.set.call_count == 1
        assert commits == []
        assert merges is None

    def test_on_idle_with_no_commits_and_no_merges(self):
        mocked_somebody_is_writing = MagicMock()
        mocked_want_to_merge = MagicMock()
        mocked_merge = MagicMock()
        mocked_push = MagicMock()

        mocked_want_to_merge.is_set.return_value = True
        mocked_somebody_is_writing.is_set.return_value = False

        worker = MergeWorker("name", "email", "name", "email",
                             strategy="strategy",
                             somebody_is_writing=mocked_somebody_is_writing,
                             want_to_merge=mocked_want_to_merge)
        worker.merge = mocked_merge
        worker.push = mocked_push

        commits, merges = worker.on_idle(None, None)

        assert mocked_push.call_count == 1
        assert mocked_merge.call_count == 1
        assert mocked_want_to_merge.clear.call_count == 1
        assert commits is None
        assert merges is None
