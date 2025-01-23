import unittest
from unittest.mock import patch, MagicMock
from Platform.dao.impl.redis_dao_impl import RedisDaoImpl
from redis.exceptions import RedisError

class TestRedisDaoImpl(unittest.TestCase):

    @patch("Platform.dao.impl.redis_dao_impl.get_redis_connection")
    @patch("Platform.dao.impl.redis_dao_impl.logger")
    def test_get_data_by_key_success(self, mock_logger, mock_get_redis_connection):
        """Test successful retrieval of data by key from Redis."""
        # Arrange
        key = "test-key"
        expected_data = "test-data"

        mock_redis_connection = MagicMock()
        mock_redis_connection.get.return_value = expected_data
        mock_get_redis_connection.return_value = mock_redis_connection

        redis_dao = RedisDaoImpl()

        # Act
        result = redis_dao.get_data_by_key(key)

        # Assert
        self.assertEqual(result, expected_data)
        mock_redis_connection.get.assert_called_once_with(key)
        mock_logger.debug.assert_any_call(f"fetching a specific data from redis with {key} key")

    @patch("Platform.dao.impl.redis_dao_impl.get_redis_connection")
    @patch("Platform.dao.impl.redis_dao_impl.logger")
    def test_get_data_by_key_redis_error(self, mock_logger, mock_get_redis_connection):
        """Test handling of a RedisError when getting data by key."""
        # Arrange
        key = "test-key"
        mock_redis_connection = MagicMock()
        mock_redis_connection.get.side_effect = RedisError("Redis get operation failed")
        mock_get_redis_connection.return_value = mock_redis_connection

        redis_dao = RedisDaoImpl()

        # Act & Assert
        with self.assertRaises(RedisError) as context:
            redis_dao.get_data_by_key(key)

        self.assertIn("Redis get operation failed", str(context.exception))
        mock_logger.error.assert_any_call(f"Failed to perform get Redis operation with {key} key: Redis get operation failed")

    @patch("Platform.dao.impl.redis_dao_impl.get_redis_connection")
    @patch("Platform.dao.impl.redis_dao_impl.logger")
    def test_set_data_by_key_success(self, mock_logger, mock_get_redis_connection):
        """Test successful setting of data by key in Redis."""
        # Arrange
        key = "test-key"
        data = "test-data"

        mock_redis_connection = MagicMock()
        mock_redis_connection.set.return_value = True
        mock_get_redis_connection.return_value = mock_redis_connection

        redis_dao = RedisDaoImpl()

        # Act
        result = redis_dao.set_data_by_key(key, data)

        # Assert
        self.assertTrue(result)
        mock_redis_connection.set.assert_called_once_with(key, data)

    @patch("Platform.dao.impl.redis_dao_impl.get_redis_connection")
    @patch("Platform.dao.impl.redis_dao_impl.logger")
    def test_set_data_by_key_redis_error(self, mock_logger, mock_get_redis_connection):
        """Test handling of a RedisError when setting data by key."""
        # Arrange
        key = "test-key"
        data = "test-data"

        mock_redis_connection = MagicMock()
        mock_redis_connection.set.side_effect = RedisError("Redis set operation failed")
        mock_get_redis_connection.return_value = mock_redis_connection

        redis_dao = RedisDaoImpl()

        # Act & Assert
        with self.assertRaises(RedisError) as context:
            redis_dao.set_data_by_key(key, data)

        self.assertIn("Redis set operation failed", str(context.exception))
        mock_logger.error.assert_any_call(f"Failed to perform set Redis operation for {key} key: Redis set operation failed")

    @patch("Platform.dao.impl.redis_dao_impl.get_redis_connection")
    @patch("Platform.dao.impl.redis_dao_impl.logger")
    def test_set_data_by_key_with_expiry_success(self, mock_logger, mock_get_redis_connection):
        """Test successful setting of data by key with an expiry in Redis."""
        # Arrange
        key = "test-key"
        data = "test-data"
        expiry = 3600

        mock_redis_connection = MagicMock()
        mock_redis_connection.setex.return_value = True
        mock_get_redis_connection.return_value = mock_redis_connection

        redis_dao = RedisDaoImpl()

        # Act
        result = redis_dao.set_data_by_key_with_expiry(key, data, expiry)

        # Assert
        self.assertTrue(result)
        mock_redis_connection.setex.assert_called_once_with(key, expiry, data)

    @patch("Platform.dao.impl.redis_dao_impl.get_redis_connection")
    @patch("Platform.dao.impl.redis_dao_impl.logger")
    def test_set_data_by_key_with_expiry_redis_error(self, mock_logger, mock_get_redis_connection):
        """Test handling of a RedisError when setting data by key with an expiry."""
        # Arrange
        key = "test-key"
        data = "test-data"
        expiry = 3600

        mock_redis_connection = MagicMock()
        mock_redis_connection.setex.side_effect = RedisError("Redis setex operation failed")
        mock_get_redis_connection.return_value = mock_redis_connection

        redis_dao = RedisDaoImpl()

        # Act & Assert
        with self.assertRaises(RedisError) as context:
            redis_dao.set_data_by_key_with_expiry(key, data, expiry)

        self.assertIn("Redis setex operation failed", str(context.exception))
        mock_logger.error.assert_any_call(f"Failed to perform set Redis operation for {key} key: Redis setex operation failed")
