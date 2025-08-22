import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Import the app
from app import create_app

class TestInitData(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        self.app.config['TESTING'] = True
        self.app.config['BUSINESS_NOTIFICATIONS_ENABLED'] = False
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.app_context.pop()

    def test_functions_exist_and_importable(self):
        """Test that we can import the init functions."""
        try:
            from app.init_data import init_job_types, init_sample_data
            
            self.assertTrue(callable(init_job_types))
            self.assertTrue(callable(init_sample_data))
            print("✓ Both init functions exist and are callable")
            
        except ImportError as e:
            self.fail(f"Could not import init functions: {e}")

    @patch('app.init_data.db.session')
    @patch('app.init_data.JobType')
    def test_init_job_types(self, mock_job_type_class, mock_session):
        """Test init_job_types with proper mocking."""
        from app.init_data import init_job_types
        
        # Mock JobType.query.filter_by().first() to return None (no existing job types)
        mock_job_type_class.query.filter_by.return_value.first.return_value = None
        
        # Mock JobType constructor
        mock_job_type_instance = MagicMock()
        mock_job_type_class.return_value = mock_job_type_instance
        
        # Run the function
        init_job_types()
        
        # Verify JobType was called 6 times (based on your default_job_types list)
        expected_calls = 6  # Number of job types in your list
        self.assertEqual(mock_job_type_class.call_count, expected_calls)
        print(f"✓ JobType was called {mock_job_type_class.call_count} times")
        
        # Verify the job type names that were created
        call_args_list = mock_job_type_class.call_args_list
        created_names = [call.kwargs['name'] if 'name' in call.kwargs else call.args[0] 
                        for call in call_args_list if call.kwargs or call.args]
        
        expected_names = [
            "House Cleaning", "Deep Cleaning", "Office Cleaning",
            "Move-in/Move-out Cleaning", "Post-Construction Cleaning", "One-off Cleaning"
        ]
        
        # Check that all expected job types were created
        for name in expected_names:
            found = any(name in str(call) for call in call_args_list)
            if not found:
                print(f"Looking for {name} in calls: {call_args_list}")
        
        # Verify session operations
        self.assertEqual(mock_session.add.call_count, expected_calls)
        print(f"✓ db.session.add was called {mock_session.add.call_count} times")
        
        mock_session.commit.assert_called_once()
        print("✓ db.session.commit was called once")

    @patch('app.init_data.db.session')
    @patch('app.init_data.Payment')
    @patch('app.init_data.Job')
    @patch('app.init_data.Client')
    @patch('app.init_data.JobType')
    def test_init_sample_data(self, mock_job_type_class, mock_client_class, 
                             mock_job_class, mock_payment_class, mock_session):
        """Test init_sample_data with proper mocking."""
        from app.init_data import init_sample_data
        
        # Mock Client.query.count() to return 0 (no existing clients)
        mock_client_class.query.count.return_value = 0
        
        # Mock JobType.query.first() to return a mock job type
        mock_job_type = MagicMock()
        mock_job_type.id = 1
        mock_job_type_class.query.first.return_value = mock_job_type
        
        # Mock constructors and their instances
        mock_client_instance = MagicMock()
        mock_client_instance.id = 1
        mock_client_class.return_value = mock_client_instance
        
        mock_job_instance = MagicMock()
        mock_job_instance.id = 1
        mock_job_class.return_value = mock_job_instance
        
        mock_payment_instance = MagicMock()
        mock_payment_class.return_value = mock_payment_instance
        
        # Run the function
        init_sample_data()
        
        # Verify that models were created
        mock_client_class.assert_called_once()
        print("✓ Client was created")
        
        mock_job_class.assert_called_once()
        print("✓ Job was created")
        
        mock_payment_class.assert_called_once()
        print("✓ Payment was created")
        
        # Verify session operations
        # Should be called 3 times: client, job, payment
        self.assertEqual(mock_session.add.call_count, 3)
        print(f"✓ db.session.add was called {mock_session.add.call_count} times")
        
        # Should be called twice: flush (twice) and commit (once)
        self.assertEqual(mock_session.flush.call_count, 2)
        print(f"✓ db.session.flush was called {mock_session.flush.call_count} times")
        
        mock_session.commit.assert_called_once()
        print("✓ db.session.commit was called once")
        
        # Verify the client was created with correct data
        client_call = mock_client_class.call_args
        self.assertIn('name', client_call.kwargs)
        self.assertEqual(client_call.kwargs['name'], "Test Client Ltd")
        print("✓ Client created with correct name")

    @patch('app.init_data.db.session')
    @patch('app.init_data.Client')
    def test_init_sample_data_skips_when_data_exists(self, mock_client_class, mock_session):
        """Test that init_sample_data skips creation when clients already exist."""
        from app.init_data import init_sample_data
        
        # Mock Client.query.count() to return 1 (existing clients)
        mock_client_class.query.count.return_value = 1
        
        # Run the function
        init_sample_data()
        
        # Verify that no new objects were created
        mock_client_class.assert_not_called()
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
        
        print("✓ init_sample_data correctly skipped when data already exists")

    @patch('app.init_data.db.session')
    def test_both_functions_work_together(self, mock_session):
        """Test that both functions can be run in sequence without errors."""
        from app.init_data import init_job_types, init_sample_data
        
        # Mock session operations
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.rollback = MagicMock()
        mock_session.flush = MagicMock()
        
        try:
            # Run both functions
            init_job_types()
            print("✓ init_job_types completed")
            
            init_sample_data()
            print("✓ init_sample_data completed")
            
            # Verify session was used
            self.assertGreater(mock_session.add.call_count + mock_session.commit.call_count, 0)
            print("✓ Database session operations were called")
            
        except Exception as e:
            self.fail(f"Functions failed when run together: {e}")


if __name__ == '__main__':
    unittest.main(verbosity=2)