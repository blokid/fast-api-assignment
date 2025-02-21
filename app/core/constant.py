# Messages

# SUCCESS
SUCCESS_SIGN_IN = "Signed in successfully."
SUCCESS_SIGN_UP = (
    "Signed up successfully. Please check your mailbox to verify your email"
)
SUCCESS_GET_USERS = "Filtered users."
SUCCESS_MATCHED_USER_ID = "The user who matched with ID."
SUCCESS_MATCHED_USER_TOKEN = "The user who matched with token."
SUCCESS_MATCHED_USER_EMAIL = "The user who matched with email."
SUCCESS_UPDATE_USER = "Updated user data successfully."
SUCCESS_DELETE_USER = "Deleted user successfully."
SUCCESS_VERIFICATION_COMPLETED = (
    "Email verification successful. Please sign in with your user email"
)

SUCCESS_GET_ORGANIZATIONS = "Filtered organizations."
SUCCESS_CREATE_ORGANIZATION = "Organization created successfully."
SUCCESS_UPDATE_ORGANIZATION = "Organization updated successfully."
SUCCESS_DELETE_ORGANIZATION = "Organization deleted successfully."
SUCCESS_MATCHED_ORGANIZATION_ID = "Organization matched with the provided ID."

SUCCESS_GET_WEBSITES = "Filtered websites."
SUCCESS_CREATE_WEBSITE = "Website created successfully."
SUCCESS_UPDATE_WEBSITE = "Website updated successfully."
SUCCESS_DELETE_WEBSITE = "Website deleted successfully."
SUCCESS_MATCHED_WEBSITE_ID = "Website matched with the provided ID."
SUCCESS_ADD_WEBSITE_MEMBER = "Website member added successfully."
SUCCESS_REMOVE_WEBSITE_MEMBER = "Website member removed successfully."
SUCCESS_GET_WEBSITE_MEMBERS = "Filtered website members."

# FAIL
FAIL_VALIDATION_USER_DUPLICATED = "There is a duplicate user already."
FAIL_VALIDATION_USER_WRONG_PASSWORD = "Invalid user password."
FAIL_VALIDATION_USER_DELETED = "The user is deleted."
FAIL_VALIDATION_MATCHED_USER_TOKEN = "No user matched with token."
FAIL_VALIDATION_MATCHED_USER_EMAIL = "No user matched with email."
FAIL_VALIDATION_MATCHED_USER_ID = "No user matched with ID."
FAIL_VALIDATION_MATCHED_FILTERED_USERS = "There are no user lists matched filter."
FAIL_VALIDATION_USER_NOT_VERIFIED = (
    "Email is not verified. Please verify your email before signing in."
)
FAIL_VALIDATION_MATCHED_FILTERED_ORGANIZATIONS = "No organizations matched the filter."
FAIL_VALIDATION_ORGANIZATION_NOT_FOUND = "No organization matched with ID"
FAIL_VALIDATION_MATCHED_ORGANIZATION_ID = (
    "No organization matched with the provided ID."
)
FAIL_USER_NOT_FOUND = "Unable to find user"
FAIL_AUTH_CHECK = "Authentication required."
FAIL_AUTH_INVALID_TOKEN_PREFIX = "Invalid Token prefix."
FAIL_AUTH_VALIDATION_CREDENTIAL = "Couldn't validate credentials."
FAIL_INVALID_VERIFICATION_TOKEN = "Invalid verification token"
FAIL_ALREADY_VERIFIED = "User is already verified"
FAIL_INSUFFICIENT_PREVILEGES = "Insufficient privileges"

FAIL_VALIDATION_WEBSITE_DUPLICATED = (
    "A website with the same name or URL already exists."
)
FAIL_VALIDATION_WEBSITE_NOT_FOUND = "No website matched with the provided ID."
FAIL_VALIDATION_MATCHED_FILTERED_WEBSITES = "No websites matched the provided filter."
FAIL_VALIDATION_MATCHED_WEBSITE_ID = "No website matched with the provided ID."
FAIL_VALIDATION_WEBSITE_MEMBER_NOT_FOUND = "The website member was not found."
FAIL_VALIDATION_WEBSITE_ROLE_INVALID = "Invalid role for website membership."
FAIL_VALIDATION_WEBSITE_MEMBER_EXISTS = "The user is already a member of this website."
FAIL_VALIDATION_WEBSITE_CREATION_FAILED = "Failed to create the website."
FAIL_VALIDATION_WEBSITE_UPDATE_FAILED = "Failed to update the website."
FAIL_VALIDATION_WEBSITE_DELETION_FAILED = "Failed to delete the website."


# EMAIL
SENDER_EMAIL = "fast-api-test@gmail.com"
VERIFICATION_EMAIL_SUBJECT = "Welcome! Verify your email"
EMAIL_VERIFICATION_ROUTE = "/auth/verify"

# OTHERS
DEFAULT_ORG_NAME_POSTFIX = " company"
