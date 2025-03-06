class ModuleDocFragment(object):
    DOCUMENTATION = r"""
    options:
      name:
        type: str
        required: true
        aliases:
        - claim_name
        description: The name of the custom claim.
      group:
        type: str
        required: true
        aliases:
        - claim_group
        description: The group to which the custom claim applies.
      values:
        type: list
        elements: str
        required: true
        description: The values for the custom claim.
    """
