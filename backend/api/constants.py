from datetime import timedelta

# Time period for updating user's last_modified timestamp to reduce database writes
USER_LAST_MODIFIED_UPDATE_INTERVAL = timedelta(minutes=1)

# Time period after which inactive users will be considered for cleanup
USER_INACTIVITY_EXPIRY_INTERVAL = timedelta(days=30)  # 1 month
