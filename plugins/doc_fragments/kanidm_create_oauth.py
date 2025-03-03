from ..module_utils.kanidm.arg_specs import KanidmOauthArgs


class ModuleDocFragment:
    # This is the main documentation for the module which is displayed in ansible-doc.
    DOCUMENTATION = KanidmOauthArgs.documentation()
