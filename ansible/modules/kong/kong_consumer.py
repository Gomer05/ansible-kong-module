from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dotdiff import dotdiff
from ansible.module_utils.kong.consumer import KongConsumer
from ansible.module_utils.kong.helpers import *

DOCUMENTATION = '''
---
module: kong_consumer
short_description: Configure a Kong Consumer object.
'''

EXAMPLES = '''
Setting custom_id's on Consumers is currently not supported;
their usefulness is limited, and they require more lookups (round-trips)
for actions that require either a username or the consumer's UUID.

- name: Configure a Consumer
  kong_consumer:
    kong_admin_uri: http://localhost:8001
    username: apiconsumer
    state: present

- name: Configure a list of Consumers
  kong_consumer:
    kong_admin_uri: http://localhost:8001
    username:
      - one
      - two
      - three
      - apiconsumers
    state: present


- name: Delete a Consumer
  kong_consumer:
    kong_admin_uri: http://localhost:8001
    username: apiconsumer
    state: absent
'''


def main():
    ansible_module = AnsibleModule(
        argument_spec=dict(
            kong_admin_uri=dict(required=True, type='str'),
            kong_admin_username=dict(required=False, type='str'),
            kong_admin_password=dict(required=False, type='str', no_log=True),
            username=dict(required=True, type='list'),
            tags=dict(required=False, type='list'),
            state=dict(required=False, default="present", choices=['present', 'absent'], type='str'),
        ),
        supports_check_mode=True
    )

    # We don't support custom_id, as its use is too limited in terms of querying
    # the Kong API. The custom_id is not a primary key, cannot be used as an index
    # in many operations, though it's marked as UNIQUE.

    # Initialize output dictionary
    result = {}

    # Admin endpoint & auth
    url = ansible_module.params['kong_admin_uri']
    auth_user = ansible_module.params['kong_admin_username']
    auth_pass = ansible_module.params['kong_admin_password']

    # Extract other arguments
    state = ansible_module.params['state']
    users = ansible_module.params['username']
    tags = ansible_module.params['tags']

    api_fields = [
        'name',
        'tags'
    ]

    # Extract api_fields from module parameters into separate dictionary
    data = params_fields_lookup(ansible_module, api_fields)

    # Create KongAPI client instance
    k = KongConsumer(url, auth_user=auth_user, auth_pass=auth_pass)

    # Contact Kong status endpoint
    kong_status_check(k, ansible_module)

    # Default return values
    changed = False
    resp = ''
    diff = []

    # Ensure the Consumer(s) are registered in Kong
    if state == "present":

        for username in users:

            orig = k.consumer_get(username)
            if orig is not None:
                # Diff the remote Consumer object against the target data if it already exists
                consumer_diff = dotdiff(orig, data)
                resp = orig
                # Set changed flag if there's a diff
                if consumer_diff:
                    data['username'] = orig['username']
                    # Log modified state and diff result
                    changed = True
                    result['state'] = 'modified'
                    result['diff'] = [dict(prepared=render_list(consumer_diff))]

            else:
                # We're inserting a new Consumer, set changed
                data['username'] = username
                changed = True
                result['state'] = 'created'
                result['diff'] = dict(
                    before_header='<undefined>', before='<undefined>\n',
                    after_header=username, after=data
                )

            # Only make changes when Ansible is not run in check mode
            if not ansible_module.check_mode and changed:
                try:
                    resp = k.consumer_apply(**data)
                except Exception as e:
                    err_msg = "Consumer configuration rejected by Kong: '{}'. " \
                              "Please check configuration of the API you are trying to configure."
                    ansible_module.fail_json(msg=err_msg.format(e))

    # Ensure the Consumer is deleted
    if state == "absent":

        for username in users:
            # Check if the Consumer exists
            orig = k.consumer_get(username)

            # Predict a change if the Consumer is present
            if orig:
                changed = True
                result['state'] = 'deleted'

                diff.append(dict(
                    before_header=username, before=orig,
                    after_header='<deleted>', after='\n'
                ))

            # Only make changes when Ansible is not run in check mode
            if not ansible_module.check_mode and orig:
                # Issue delete call to the Kong API
                try:
                    resp = k.consumer_delete(username)
                except Exception as e:
                    ansible_module.fail_json(msg='Error deleting Consumer: {}'.format(e))

    # Pass through the API response if non-empty
    if resp:
        result['response'] = resp

    # Pass through the diff result
    if diff:
        result['diff'] = diff

    # Prepare module output
    result.update(
        dict(
            changed=changed,
        )
    )

    ansible_module.exit_json(**result)


if __name__ == '__main__':
    main()