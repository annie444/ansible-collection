class ModuleDocFragment(object):
    DOCUMENTATION = r"""
    options:
      name:
        type: str
        required: true
        aliases:
        - client_name
        description: The name of the OAuth client.
      url:
        type: str
        required: true
        aliases:
        - client_url
        description: The URL of the OAuth client's landing page.
      redirect_url:
        type: list
        elements: str
        required: true
        aliases:
        - redirect_urls
        description: The redirect URLs for the OAuth client.
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
        aliases:
        - scope
        description: The scopes requested by the OAuth client.
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
      display_name:
        type: str
        required: false
        aliases:
        - client_display_name
        default: '{{ name }}'
        description: The display name of the OAuth client.
      group:
        type: str
        default: idm_all_persons
        required: false
        description: The group associated with the OAuth client. Defaults to all persons.
      public:
        type: bool
        default: false
        required: false
        description: Indicates if the client is public.
      claim_join:
        type: str
        choices:
        - array
        - csv
        - ssv
        default: array
        required: false
        description: How to join claims in the response. Defaults to array.
      pkce:
        type: bool
        default: true
        required: false
        description: Indicates if PKCE is enabled.
      legacy_crypto:
        type: bool
        default: false
        required: false
        description: Indicates if legacy cryptography is used.
      strict_redirect:
        type: bool
        default: true
        required: false
        description: Indicates if strict redirect validation is enabled.
      local_redirect:
        type: bool
        default: false
        required: false
        description: Indicates if local redirects are allowed.
      sup_scopes:
        type: list
        elements: dict
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
        required: false
        description: Additional scopes for specific groups.
      username:
        type: str
        choices:
        - spn
        - short
        default: spn
        required: false
        description: Preferred username format. Defaults to SPN which takes the format of
          '<username>@<kanidm.uri>'.
      custom_claims:
        type: list
        elements: dict
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
        required: false
        description: Custom claims to be included in the OAuth response.
      image:
        type: dict
        options:
          src:
            type: str
            required: true
            aliases:
            - image_src
            description: The source URL of the image.
          format:
            type: str
            choices:
            - png
            - jpg
            - gif
            - svg
            - webp
            - auto
            default: auto
            required: false
            description: The format of the image. Defaults to auto.
        required: false
        aliases:
        - logo
        description: Image configuration for the OAuth client.
      debug:
        type: bool
        default: false
        required: false
        description: Enable debug mode.
    """
