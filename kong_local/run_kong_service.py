from kong_local.kong.service import KongService

# Initialize output dictionary
result = {}

# Admin endpoint & auth
url = "http://127.0.0.1:8001"
auth_user = "kong_admin"
auth_pass = "kong123"

# Extract arguments
state = "present"
# protocols = ['http']
name = "lsl-dev-member-profile"
host = "member-profile.app.internal"
config = {}
tags = ["test_tag", "service_tag1"]

def main():
    # Create KongAPI client instance
    k = KongService(url, auth_user=auth_user, auth_pass=auth_pass)

    # Check if the Plugin is already present
    pq = k.service_list()
    print(f"Got services: {pq}")

    pq = k.service_get(name=name)
    print(f"Got service: {pq}")

    pq = k.service_apply(name=name, host=host, port=None, protocol=None, path=None, retries=None, connect_timeout=None,
                      write_timeout=None, read_timeout=None, tags=tags)
    print(f"Applied to service: {pq}")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
