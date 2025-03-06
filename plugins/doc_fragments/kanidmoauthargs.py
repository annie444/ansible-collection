class ModuleDocFragment(object):
    DOCUMENTATION = r"""
    options:
      name:
        type: str
        required: true
        aliases:
        - client_name
        documentation: The name of the OAuth client.
      url:
        type: str
        required: true
        aliases:
        - client_url
        documentation: The URL of the OAuth client's landing page.
      redirect_url:
        type: list
        elements: str
        required: true
        aliases:
        - redirect_urls
        documentation: The redirect URLs for the OAuth client.
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
        documentation: The scopes requested by the OAuth client.
      kanidm:
        type: dict
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
        required: true
        documentation: Configuration for the Kanidm client.
      display_name:
        type: str
        required: false
        aliases:
        - client_display_name
        default: '{{ name }}'
        documentation: The display name of the OAuth client.
      group:
        type: str
        default: idm_all_persons
        required: false
        documentation: The group associated with the OAuth client. Defaults to all persons.
      public:
        type: bool
        default: false
        required: false
        documentation: Indicates if the client is public.
      claim_join:
        type: str
        choices:
        - array
        - csv
        - ssv
        default: array
        required: false
        documentation: How to join claims in the response. Defaults to array.
      pkce:
        type: bool
        default: true
        required: false
        documentation: Indicates if PKCE is enabled.
      legacy_crypto:
        type: bool
        default: false
        required: false
        documentation: Indicates if legacy cryptography is used.
      strict_redirect:
        type: bool
        default: true
        required: false
        documentation: Indicates if strict redirect validation is enabled.
      local_redirect:
        type: bool
        default: false
        required: false
        documentation: Indicates if local redirects are allowed.
      sup_scopes:
        type: list
        elements: dict
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
        required: false
        documentation: Additional scopes for specific groups.
      username:
        type: str
        choices:
        - spn
        - short
        default: spn
        required: false
        documentation: Preferred username format. Defaults to SPN which takes the format
          of '<username>@<kanidm.uri>'.
      custom_claims:
        type: list
        elements: dict
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
        required: false
        documentation: Custom claims to be included in the OAuth response.
      image:
        type: dict
        options:
          src:
            type: str
            required: true
            aliases:
            - image_src
            documentation: The source URL of the image.
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
            documentation: The format of the image. Defaults to auto.
        required: false
        aliases:
        - logo
        documentation: Image configuration for the OAuth client.
      debug:
        type: bool
        default: false
        required: false
        documentation: Enable debug mode.
    """

