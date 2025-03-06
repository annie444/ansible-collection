class ModuleDocFragment(object):
    DOCUMENTATION = r"""
    options:
      name:
        type: str
        required: true
        aliases:
        - claim_name
        documentation: The name of the custom claim.
      group:
        type: str
        required: true
        aliases:
        - claim_group
        documentation: The group to which the custom claim applies.
      values:
        type: list
        elements: str
        required: true
        documentation: The values for the custom claim.
    """