class ModuleDocFragment(object):
    DOCUMENTATION = r"""
    options:
      group:
        type: str
        required: true
        aliases:
        - sup_scope_group
        description: The group to which the additional scopes apply.
      scopes:
        type: list
        elements: str
        choices:
        - openid
        - profile
        - email
        - address
        - phone
        - groups
        - ssh_publickeys
        required: true
        description: The additional scopes for the group.
    """
