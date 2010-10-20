from django.test import TestCase

from djexceptional.utils import memoize


class MemoizeTest(TestCase):

    def test_no_args(self):
        """Test @memoize on functions without any arguments."""

        counter = []
        def increment_counter():
            counter.append(None)
            return len(counter)

        self.assertEqual(len(counter), 0)
        self.assertEqual(increment_counter(), 1)
        self.assertEqual(len(counter), 1)
        self.assertEqual(increment_counter(), 2)
        self.assertEqual(len(counter), 2)

        increment_counter = memoize(increment_counter)

        self.assertEqual(increment_counter(), 3)
        self.assertEqual(len(counter), 3)
        self.assertEqual(increment_counter(), 3)
        self.assertEqual(len(counter), 3)

    def test_args(self):
        """Test @memoize on functions with arguments."""

        counter = []
        def sum_squared(x, y):
            counter.append(None)
            return x ** 2 + y ** 2

        self.assertEqual(len(counter), 0)
        self.assertEqual(sum_squared(3, 4), 25)
        self.assertEqual(len(counter), 1)
        self.assertEqual(sum_squared(4, 5), 41)
        self.assertEqual(len(counter), 2)

        sum_squared = memoize(sum_squared)

        self.assertEqual(sum_squared(3, 4), 25)
        self.assertEqual(len(counter), 3)
        self.assertEqual(sum_squared(3, 4), 25)
        self.assertEqual(sum_squared(3, 4), 25)
        self.assertEqual(sum_squared(3, 4), 25)
        self.assertEqual(len(counter), 3)

        self.assertEqual(sum_squared(4, 5), 41)
        self.assertEqual(len(counter), 4)
        self.assertEqual(sum_squared(4, 5), 41)
        self.assertEqual(sum_squared(4, 5), 41)
        self.assertEqual(sum_squared(4, 5), 41)
        self.assertEqual(len(counter), 4)

    def test_clear(self):
        """Test the `clear()` method added to wrapped functions."""

        counter = []
        def increment_counter():
            counter.append(None)
            return len(counter)
        increment_counter = memoize(increment_counter)

        self.assertEqual(len(counter), 0)
        self.assertEqual(increment_counter(), 1)
        self.assertEqual(len(counter), 1)
        self.assertEqual(increment_counter(), 1)
        self.assertEqual(increment_counter(), 1)
        self.assertEqual(increment_counter(), 1)
        self.assertEqual(len(counter), 1)

        increment_counter.clear()

        self.assertEqual(increment_counter(), 2)
        self.assertEqual(len(counter), 2)
        self.assertEqual(increment_counter(), 2)
        self.assertEqual(increment_counter(), 2)
        self.assertEqual(increment_counter(), 2)
        self.assertEqual(len(counter), 2)
