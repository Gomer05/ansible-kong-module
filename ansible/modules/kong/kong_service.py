#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dotdiff import dotdiff
from ansible.module_utils.kong.service import KongService
from ansible.module_utils.kong.helpers import *


#
# This code is a modified version of https://github.com/4finance/ansible-modules-kong
#
# This is a free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This Ansible library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.
ANSIBLE_METADATA = {'metadata_version': '0.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: kong_service
short_description: Configure a Kong Service object.
'''

EXAMPLES = '''
- name: Configure an Service
  kong_service:
    kong_admin_uri: http://localhost:8001
    kong_admin_password: <password_here>
    name: Mockbin
    protocol: http
    host: mockbin.org
    state: present
'''


def main():
    ansible_module = AnsibleModule(
        argument_spec=dict(
            kong_admin_uri=dict(required=True, type='str'),
            kong_admin_username=dict(required=False, type='str'),
            kong_admin_password=dict(required=False, type='str', no_log=True),
            name=dict(required=True, type='str'),
            protocol=dict(required=False, default="http", choices=['http', 'https'], type='str'),
            host=dict(required=True, type='str'),
            port=dict(required=False, default=80, type='int'),
            path=dict(required=False, type='str'),
            tags=dict(required=False, type='list'),
            retries=dict(required=False, default=5, type='int'),
            connect_timeout=dict(required=False, default=60000, type='int'),
            write_timeout=dict(required=False, default=60000, type='int'),
            read_timeout=dict(required=False, default=60000, type='int'),
            state=dict(required=False, default="present", choices=['present', 'absent'], type='str'),
        ),
        required_if=[
            ('state', 'present', ['host', 'name'])
        ],
        supports_check_mode=True
    )

    # Initialize output dictionary
    result = {}

    # Kong 0.14.x
    api_fields = [
        'name',
        'protocol',
        'host',
        'port',
        'path',
        'retries',
        'connect_timeout',
        'write_timeout',
        'read_timeout',
        'tags'
    ]

    # Extract api_fields from module parameters into separate dictionary
    data = params_fields_lookup(ansible_module, api_fields)

    # Admin endpoint & auth
    url = ansible_module.params['kong_admin_uri']
    auth_user = ansible_module.params['kong_admin_username']
    auth_pass = ansible_module.params['kong_admin_password']

    # Extract other arguments
    state = ansible_module.params['state']
    name = ansible_module.params['name']

    # Create KongService client instance
    k = KongService(url, auth_user=auth_user, auth_pass=auth_pass)

    # Contact Kong status endpoint
    kong_status_check(k, ansible_module)

    # Default return values
    changed = False
    resp = ''

    # Ensure the service is registered in Kong
    if state == "present":

        # Check if the service exists
        orig = k.service_get(name)
        if orig is not None:

            # Diff the remote API object against the target data if it already exists
            servicediff = dotdiff(orig, data)

            # Set changed flag if there's a diff
            if servicediff:
                # Log modified state and diff result
                changed = True
                result['state'] = 'modified'
                result['diff'] = [dict(prepared=render_list(servicediff))]

        else:
            # We're inserting a new service, set changed
            changed = True
            result['state'] = 'created'
            result['diff'] = dict(
                before_header='<undefined>', before='<undefined>\n',
                after_header=name, after=data
            )

        # Only make changes when Ansible is not run in check mode
        if not ansible_module.check_mode and changed:
            try:
                resp = k.service_apply(**data)
            except Exception as e:
                app_err = "Service configuration rejected by Kong: '{}'. " \
                          "Please check configuration of the service you are trying to configure."
                ansible_module.fail_json(msg=app_err.format(e))

    # Ensure the service is deleted
    if state == "absent":

        # Check if the service exists
        orig = k.service_get(name)

        # Predict a change if the service exists
        if orig:
            changed = True
            result['state'] = 'deleted'
            result['diff'] = dict(
                before_header=name, before=orig,
                after_header='<deleted>', after='\n'
            )

        # Only make changes when Ansible is not run in check mode
        if not ansible_module.check_mode and orig:
            # Issue delete call to the Kong service
            try:
                resp = k.service_delete(name)
            except Exception as e:
                ansible_module.fail_json(msg='Error deleting service: {}'.format(e))

    # Pass through the API response if non-empty
    if resp:
        result['response'] = resp

    # Prepare module output
    result.update(
        dict(
            changed=changed,
        )
    )

    ansible_module.exit_json(**result)


if __name__ == '__main__':
    main()
