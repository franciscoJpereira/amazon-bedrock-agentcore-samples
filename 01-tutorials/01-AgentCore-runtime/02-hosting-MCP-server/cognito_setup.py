from utils import setup_cognito_user_pool
def setup():
    print("Setting up Amazon Cognito user pool...")
    cognito_config = setup_cognito_user_pool()
    print("Cognito setup completed ✓")
    print(f"User Pool ID: {cognito_config.get('user_pool_id', 'N/A')}")
    print(f"Client ID: {cognito_config.get('client_id', 'N/A')}")

if __name__ == "__main__":
    setup()