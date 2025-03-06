class ModuleDocFragment(object):
    DOCUMENTATION = r"""
    options:
      group:
        type: str
        required: true
        aliases:
        - sup_scope_group
        documentation: The group to which the additional scopes apply.
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
        documentation: The additional scopes for the group.
    """