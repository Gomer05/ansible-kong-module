from kong_local.kong.consumer import KongConsumer

# Initialize output dictionary
result = {}

# Admin endpoint & auth
url = "http://127.0.0.1:8001"
auth_user = "kong_admin"
auth_pass = "kong123"

# Extract arguments
state = "present"
#consumer_id = ""
#custom_id = ""
username = "test01"
tags = ["test_tag", "service_tag1"]

def main():
    # Create KongAPI client instance
    k = KongConsumer(url, auth_user=auth_user, auth_pass=auth_pass)

    # Check if the Plugin is already present
    list = k.consumer_list()
    print(f"Got consumers: {list}")

    pq = k.consumer_get(username)
    print(f"got consumer by username: {pq}")

    pq = k.consumer_apply(username=username, custom_id=None, tags=tags)
    print(f"user: {pq}")

    delete = k.consumer_delete("mark")
    print(f"deleted: {delete}")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
