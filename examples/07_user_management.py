"""User management: List users, inspect roles, and (optionally) create a new user.

Shows how to enumerate users and roles, then demonstrates creating a user
and assigning them access to specific locations.

Usage:
    export LISTINGSAPI_KEY="your_api_key"
    python 07_user_management.py
"""

import listingsapi

client = listingsapi.ListingsAPI()

# List current users
users = client.users.list()
print(f"Current users ({len(users)}):")
for user in users:
    role_name = getattr(getattr(user, "role", None), "name", "N/A")
    print(f"  {user.email} -- {user.firstName} {getattr(user, 'lastName', '')} (role: {role_name})")

# List available roles
roles = client.users.roles()
print(f"\nAvailable roles ({len(roles)}):")
for role in roles:
    print(f"  {role.name} (id: {role.id})")

# Create a new user (uncomment to run)
# role_id = roles[0].id
# result = client.users.create(
#     email="newuser@example.com",
#     role_id=role_id,
#     first_name="New",
#     last_name="User",
# )
# print(f"\nCreated user: {result.to_dict()}")
#
# # Assign locations to the new user
# user_id = result.get("id") or result.get("user", {}).get("id")
# if user_id:
#     page = client.locations.list(first=5)
#     loc_ids = [loc.id for loc in page]
#     client.users.add_locations(user_id, loc_ids)
#     print(f"Assigned {len(loc_ids)} locations to user")
