import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add api directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../api')))

# Mock CosmosDBService before importing auth_service
with patch('shared.cosmos_db.CosmosDBService') as MockCosmos:
    mock_container = MagicMock()
    mock_container.query_items.return_value = [] # No existing users/credentials
    mock_container.upsert_item.return_value = {}
    
    mock_instance = MockCosmos.return_value
    mock_instance.get_users_container.return_value = mock_container
    mock_instance.get_credentials_container.return_value = mock_container
    
    # Mock os.getenv to avoid errors in initialization
    with patch.dict(os.environ, {"RP_ID": "localhost", "RP_ORIGIN": "http://localhost:5173"}):
        from shared.auth_service import auth_service

        def test_registration_options():
            print("Testing Registration Options Generation...")
            try:
                options = auth_service.generate_registration_options("testuser", "Test User")
                options_dict = json.loads(options)
                
                assert "rp" in options_dict
                assert options_dict["rp"]["id"] == "localhost"
                assert "user" in options_dict
                assert options_dict["user"]["name"] == "testuser"
                assert "challenge" in options_dict
                print("✅ Registration options generated successfully")
                return True
            except Exception as e:
                print(f"❌ Registration options failed: {e}")
                return False

        def test_login_options():
            print("\nTesting Login Options Generation...")
            try:
                # Mock get_user to return a user
                with patch.object(auth_service, 'get_user') as mock_get_user:
                    mock_get_user.return_value = {"id": "testuser", "username": "testuser"}
                    
                    options = auth_service.generate_login_options("testuser")
                    options_dict = json.loads(options)
                    
                    assert "rpId" in options_dict
                    assert options_dict["rpId"] == "localhost"
                    assert "challenge" in options_dict
                    print("✅ Login options generated successfully")
                    return True
            except Exception as e:
                print(f"❌ Login options failed: {e}")
                return False

        if __name__ == "__main__":
            reg_success = test_registration_options()
            login_success = test_login_options()
            
            if reg_success and login_success:
                print("\n🎉 All backend auth tests passed!")
                sys.exit(0)
            else:
                print("\n⚠️ Some tests failed.")
                sys.exit(1)
