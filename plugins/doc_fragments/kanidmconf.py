class ModuleDocFragment(object):
    DOCUMENTATION = r"""
    options:
      uri:
        type: str
        required: true
        aliases:
        - kanidm_uri
        documentation: The URI of the Kanidm server.
      token:
        type: str
        required: false
        no_log: true
        aliases:
        - kanidm_token
        documentation: The token for authentication.
      ca_path:
        type: path
        required: false
        aliases:
        - kanidm_ca_path
        documentation: The path to the CA certificate.
      username:
        type: str
        required: false
        no_log: true
        aliases:
        - kanidm_username
      password:
        type: str
        required: false
        no_log: true
        aliases:
        - kanidm_password
      ca_cert_data:
        type: str
        required: false
        no_log: true
        documentation: The CA certificate data as a base64 encoded string.
      verify_ca:
        type: bool
        required: false
        default: true
        documentation: Whether to verify the Kanidm server's certificate chain.
      connect_timeout:
        type: int
        required: false
        default: 30
        documentation: The connection timeout in seconds.
    """

