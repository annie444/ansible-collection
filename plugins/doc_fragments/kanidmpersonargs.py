class ModuleDocFragment(object):
    DOCUMENTATION = r"""
    options:
      name:
        type: str
        required: true
        aliases:
        - username
        description: The username for the user.
      display_name:
        type: str
        required: false
        default: '{{ name }}'
        aliases:
        - fullname
        description: The display name of the User.
      ttl:
        type: int
        required: false
        default: 0
        description: The TTL of the credential reset token.
      kanidm:
        type: dict
        options:
          uri:
            type: str
            required: true
            aliases:
            - kanidm_uri
            description: The URI of the Kanidm server.
          token:
            type: str
            required: false
            no_log: true
            aliases:
            - kanidm_token
            description: The token for authentication.
          ca_path:
            type: path
            required: false
            aliases:
            - kanidm_ca_path
            description: The path to the CA certificate.
          username:
            type: str
            required: false
            no_log: true
            aliases:
            - kanidm_username
            description: The username for authentication.
          password:
            type: str
            required: false
            no_log: true
            aliases:
            - kanidm_password
            description: The password for authentication.
          ca_cert_data:
            type: str
            required: false
            no_log: true
            description: The CA certificate data as a base64 encoded string.
          verify_ca:
            type: bool
            required: false
            default: true
            description: Whether to verify the Kanidm server's certificate chain.
          connect_timeout:
            type: int
            required: false
            default: 30
            description: The connection timeout in seconds.
        required: true
        description: Configuration for the Kanidm client.
      debug:
        type: bool
        default: false
        required: false
        description: Enable debug mode.
      
    """

