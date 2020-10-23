from kong_local.kong.route import KongRoute

# Initialize output dictionary
result = {}

# Admin endpoint & auth
url = "http://127.0.0.1:8001"
auth_user = "kong_admin"
auth_pass = "kong123"

# Extract arguments
state = "present"
protocols = ['http']
service_name = "lsl-dev-member-profile"
hosts = ["member.app.internal"]
name = "lsl-dev-member-profile-profile"
tags = ["test_tag", "service_tag2"]

def main():
    # Create KongAPI client instance
    k = KongRoute(url, auth_user=auth_user, auth_pass=auth_pass)

    # Check if the Plugin is already present
    pq = k.route_list(service_name)
    print(f"Got routes: {pq}")

    route = k.route_get(name)
    print(f"got route: {route}")
    if route:
        route_id = route['id']
        print(f"route id: {route_id}")
        result = k.route_apply(service_name, name=name, hosts=hosts, paths=None, methods=None, protocols=protocols, strip_path=False,
                        preserve_host=False, route_id=route_id, tags=tags)
        print(f"applied to route: {result}")
    else:
        result = k.route_apply(service_name, name=name, hosts=hosts, paths=None, methods=None, protocols=protocols, strip_path=False,
                        preserve_host=False, route_id=None, tags=tags)
        print(f"applied to route: {result}")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
