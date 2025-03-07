### Because consistency is great!
###

from datetime import timedelta
import os

## The default location for the `kanidm` CLI tool's token cache.
CLIENT_TOKEN_CACHE: str = "~/.cache/kanidm_tokens"

## Content type string for jpeg
CONTENT_TYPE_JPG: str = "image/jpeg"
## Content type string for png
CONTENT_TYPE_PNG: str = "image/png"
## Content type string for gif
CONTENT_TYPE_GIF: str = "image/gif"
## Content type string for svg
CONTENT_TYPE_SVG: str = "image/svg+xml"
## Content type string for webp
CONTENT_TYPE_WEBP: str = "image/webp"

# For when the user uploads things to the various image endpoints, these are the valid content-types.
VALID_IMAGE_UPLOAD_CONTENT_TYPES: list[str] = [
    CONTENT_TYPE_JPG,
    CONTENT_TYPE_PNG,
    CONTENT_TYPE_GIF,
    CONTENT_TYPE_SVG,
    CONTENT_TYPE_WEBP,
]

APPLICATION_JSON: str = "application/json"

## The "system" path for Kanidm client config
DEFAULT_CLIENT_CONFIG_PATH: str = os.environ.get("KANIDM_CLIENT_CONFIG_PATH", "")
## The user-owned path for Kanidm client config
DEFAULT_CLIENT_CONFIG_PATH_HOME: str = "~/.config/kanidm"

## The default HTTPS bind address for the Kanidm server
DEFAULT_SERVER_ADDRESS: str = "127.0.0.1:8443"
DEFAULT_SERVER_LOCALHOST: str = "localhost:8443"
## The default LDAP bind address for the Kanidm client
DEFAULT_LDAP_LOCALHOST: str = "localhost:636"
## The default amount of attributes that can be queried in LDAP
DEFAULT_LDAP_MAXIMUM_QUERYABLE_ATTRIBUTES: int = 16
## Default replication configuration
DEFAULT_REPLICATION_ADDRESS: str = "127.0.0.1:8444"
DEFAULT_REPLICATION_ORIGIN: str = "repl:#localhost:8444"

## Default replication poll window in seconds.
DEFAULT_REPL_TASK_POLL_INTERVAL: int = 15

## Default grace window for authentication tokens. This allows a token to be
## validated by another replica before the backing database session has been
## replicated to the partner. If replication stalls until this point then
## the token will be considered INVALID.
AUTH_TOKEN_GRACE_WINDOW: timedelta = timedelta(seconds=5 * 60)

# IF YOU CHANGE THESE VALUES YOU BREAK EVERYTHING
ATTR_ACCOUNT_EXPIRE: str = "account_expire"
ATTR_ACCOUNT_VALID_FROM: str = "account_valid_from"
ATTR_ACCOUNT: str = "account"
ATTR_ACP_CREATE_ATTR: str = "acp_create_attr"
ATTR_ACP_CREATE_CLASS: str = "acp_create_class"
ATTR_ACP_ENABLE: str = "acp_enable"
ATTR_ACP_MODIFY_CLASS: str = "acp_modify_class"
ATTR_ACP_MODIFY_PRESENTATTR: str = "acp_modify_presentattr"
ATTR_ACP_MODIFY_REMOVEDATTR: str = "acp_modify_removedattr"
ATTR_ACP_RECEIVER_GROUP: str = "acp_receiver_group"
ATTR_ACP_RECEIVER: str = "acp_receiver"
ATTR_ACP_SEARCH_ATTR: str = "acp_search_attr"
ATTR_ACP_TARGET_SCOPE: str = "acp_targetscope"
ATTR_API_TOKEN_SESSION: str = "api_token_session"
ATTR_APPLICATION_PASSWORD: str = "application_password"
ATTR_ATTESTED_PASSKEYS: str = "attested_passkeys"
ATTR_ATTR: str = "attr"
ATTR_ATTRIBUTENAME: str = "attributename"
ATTR_ATTRIBUTETYPE: str = "attributetype"
ATTR_AUTH_SESSION_EXPIRY: str = "authsession_expiry"
ATTR_AUTH_PASSWORD_MINIMUM_LENGTH: str = "auth_password_minimum_length"
ATTR_BADLIST_PASSWORD: str = "badlist_password"
ATTR_CERTIFICATE: str = "certificate"
ATTR_CLAIM: str = "claim"
ATTR_CLASS: str = "class"
ATTR_CLASSNAME: str = "classname"
ATTR_CN: str = "cn"
ATTR_COOKIE_PRIVATE_KEY: str = "cookie_private_key"
ATTR_CREATED_AT_CID: str = "created_at_cid"
ATTR_CREDENTIAL_UPDATE_INTENT_TOKEN: str = "credential_update_intent_token"
ATTR_CREDENTIAL_TYPE_MINIMUM: str = "credential_type_minimum"
ATTR_DENIED_NAME: str = "denied_name"
ATTR_DESCRIPTION: str = "description"
ATTR_DIRECTMEMBEROF: str = "directmemberof"
ATTR_DISPLAYNAME: str = "displayname"
ATTR_DN: str = "dn"
ATTR_DOMAIN_ALLOW_EASTER_EGGS: str = "domain_allow_easter_eggs"
ATTR_DOMAIN_DEVELOPMENT_TAINT: str = "domain_development_taint"
ATTR_DOMAIN_DISPLAY_NAME: str = "domain_display_name"
ATTR_DOMAIN_LDAP_BASEDN: str = "domain_ldap_basedn"
ATTR_DOMAIN_NAME: str = "domain_name"
ATTR_DOMAIN_SSID: str = "domain_ssid"
ATTR_DOMAIN_TOKEN_KEY: str = "domain_token_key"
ATTR_DOMAIN_UUID: str = "domain_uuid"
ATTR_DOMAIN: str = "domain"
ATTR_DYNGROUP_FILTER: str = "dyngroup_filter"
ATTR_DYNGROUP: str = "dyngroup"
ATTR_DYNMEMBER: str = "dynmember"
ATTR_LDAP_EMAIL_ADDRESS: str = "emailaddress"
ATTR_LDAP_MAX_QUERYABLE_ATTRS: str = "ldap_max_queryable_attrs"
ATTR_EMAIL_ALTERNATIVE: str = "emailalternative"
ATTR_EMAIL_PRIMARY: str = "emailprimary"
ATTR_EMAIL: str = "email"
ATTR_ENTRYDN: str = "entrydn"
ATTR_ENTRY_MANAGED_BY: str = "entry_managed_by"
ATTR_ENTRYUUID: str = "entryuuid"
ATTR_LDAP_KEYS: str = "keys"
ATTR_LIMIT_SEARCH_MAX_RESULTS: str = "limit_search_max_results"
ATTR_LIMIT_SEARCH_MAX_FILTER_TEST: str = "limit_search_max_filter_test"
ATTR_EXCLUDES: str = "excludes"
ATTR_ES256_PRIVATE_KEY_DER: str = "es256_private_key_der"
ATTR_FERNET_PRIVATE_KEY_STR: str = "fernet_private_key_str"
ATTR_GECOS: str = "gecos"
ATTR_GIDNUMBER: str = "gidnumber"
ATTR_GRANT_UI_HINT: str = "grant_ui_hint"
ATTR_GROUP: str = "group"
ATTR_ID_VERIFICATION_ECKEY: str = "id_verification_eckey"
ATTR_IMAGE: str = "image"
ATTR_INDEX: str = "index"
ATTR_IPANTHASH: str = "ipanthash"
ATTR_IPASSHPUBKEY: str = "ipasshpubkey"
ATTR_JWS_ES256_PRIVATE_KEY: str = "jws_es256_private_key"
ATTR_KEY_ACTION_ROTATE: str = "key_action_rotate"
ATTR_KEY_ACTION_REVOKE: str = "key_action_revoke"
ATTR_KEY_ACTION_IMPORT_JWS_ES256: str = "key_action_import_jws_es256"
ATTR_KEY_INTERNAL_DATA: str = "key_internal_data"
ATTR_KEY_PROVIDER: str = "key_provider"
ATTR_LAST_MODIFIED_CID: str = "last_modified_cid"
ATTR_LDAP_ALLOW_UNIX_PW_BIND: str = "ldap_allow_unix_pw_bind"
ATTR_LEGALNAME: str = "legalname"
ATTR_LINKEDGROUP: str = "linked_group"
ATTR_LOGINSHELL: str = "loginshell"
ATTR_MAIL: str = "mail"
ATTR_MAY: str = "may"
ATTR_MEMBER: str = "member"
ATTR_MEMBEROF: str = "memberof"
ATTR_MULTIVALUE: str = "multivalue"
ATTR_MUST: str = "must"
ATTR_NAME_HISTORY: str = "name_history"
ATTR_NAME: str = "name"
ATTR_NO_INDEX: str = "no-index"
ATTR_NSACCOUNTLOCK: str = "nsaccountlock"
ATTR_NSUNIQUEID: str = "nsuniqueid"

ATTR_OAUTH2_ALLOW_INSECURE_CLIENT_DISABLE_PKCE: str = (
    "oauth2_allow_insecure_client_disable_pkce"
)
ATTR_OAUTH2_ALLOW_LOCALHOST_REDIRECT: str = "oauth2_allow_localhost_redirect"
ATTR_OAUTH2_CONSENT_SCOPE_MAP: str = "oauth2_consent_scope_map"
ATTR_OAUTH2_DEVICE_FLOW_ENABLE: str = "oauth2_device_flow_enable"
ATTR_OAUTH2_JWT_LEGACY_CRYPTO_ENABLE: str = "oauth2_jwt_legacy_crypto_enable"
ATTR_OAUTH2_PREFER_SHORT_USERNAME: str = "oauth2_prefer_short_username"
ATTR_OAUTH2_RS_BASIC_SECRET: str = "oauth2_rs_basic_secret"
ATTR_OAUTH2_RS_CLAIM_MAP: str = "oauth2_rs_claim_map"
ATTR_OAUTH2_RS_IMPLICIT_SCOPES: str = "oauth2_rs_implicit_scopes"
ATTR_OAUTH2_RS_NAME: str = "oauth2_rs_name"
ATTR_OAUTH2_RS_ORIGIN_LANDING: str = "oauth2_rs_origin_landing"
ATTR_OAUTH2_RS_ORIGIN: str = "oauth2_rs_origin"
ATTR_OAUTH2_RS_SCOPE_MAP: str = "oauth2_rs_scope_map"
ATTR_OAUTH2_RS_SUP_SCOPE_MAP: str = "oauth2_rs_sup_scope_map"
ATTR_OAUTH2_RS_TOKEN_KEY: str = "oauth2_rs_token_key"
ATTR_OAUTH2_SESSION: str = "oauth2_session"
ATTR_OAUTH2_STRICT_REDIRECT_URI: str = "oauth2_strict_redirect_uri"
ATTR_OBJECTCLASS: str = "objectclass"
ATTR_OTHER_NO_INDEX: str = "other-no-index"
ATTR_PASSKEYS: str = "passkeys"
ATTR_PASSWORD_IMPORT: str = "password_import"
ATTR_PATCH_LEVEL: str = "patch_level"
ATTR_PHANTOM: str = "phantom"
ATTR_PRIMARY_CREDENTIAL: str = "primary_credential"
ATTR_TOTP_IMPORT: str = "totp_import"
ATTR_PRIVATE_COOKIE_KEY: str = "private_cookie_key"
ATTR_PRIVILEGE_EXPIRY: str = "privilege_expiry"
ATTR_RADIUS_SECRET: str = "radius_secret"
ATTR_RECYCLED: str = "recycled"
ATTR_RECYCLEDDIRECTMEMBEROF: str = "recycled_directmemberof"
ATTR_REFERS: str = "refers"
ATTR_REPLICATED: str = "replicated"
ATTR_RS256_PRIVATE_KEY_DER: str = "rs256_private_key_der"
ATTR_SCIM_SCHEMAS: str = "schemas"
ATTR_SCOPE: str = "scope"
ATTR_SELF: str = "self"
ATTR_SOURCE_UUID: str = "source_uuid"
ATTR_SPN: str = "spn"
ATTR_SUDOHOST: str = "sudohost"
ATTR_SUPPLEMENTS: str = "supplements"
ATTR_LDAP_SSHPUBLICKEY: str = "sshpublickey"
ATTR_SSH_PUBLICKEY: str = "ssh_publickey"
ATTR_SYNC_ALLOWED: str = "sync_allowed"
ATTR_SYNC_CLASS: str = "sync_class"
ATTR_SYNC_COOKIE: str = "sync_cookie"
ATTR_SYNC_CREDENTIAL_PORTAL: str = "sync_credential_portal"
ATTR_SYNC_EXTERNAL_ID: str = "sync_external_id"
ATTR_SYNC_EXTERNAL_UUID: str = "sync_external_uuid"
ATTR_SYNC_PARENT_UUID: str = "sync_parent_uuid"
ATTR_SYNC_TOKEN_SESSION: str = "sync_token_session"
ATTR_SYNC_YIELD_AUTHORITY: str = "sync_yield_authority"
ATTR_SYNTAX: str = "syntax"
ATTR_SYSTEMEXCLUDES: str = "systemexcludes"
ATTR_SYSTEMMAY: str = "systemmay"
ATTR_SYSTEMMUST: str = "systemmust"
ATTR_SYSTEMSUPPLEMENTS: str = "systemsupplements"
ATTR_TERM: str = "term"
ATTR_UID: str = "uid"
ATTR_UIDNUMBER: str = "uidnumber"
ATTR_UNIQUE: str = "unique"
ATTR_UNIX_PASSWORD: str = "unix_password"
ATTR_UNIX_PASSWORD_IMPORT: str = "unix_password_import"
ATTR_USER_AUTH_TOKEN_SESSION: str = "user_auth_token_session"
ATTR_USERID: str = "userid"
ATTR_USERPASSWORD: str = "userpassword"
ATTR_UUID: str = "uuid"
ATTR_VERSION: str = "version"
ATTR_WEBAUTHN_ATTESTATION_CA_LIST: str = "webauthn_attestation_ca_list"
ATTR_ALLOW_PRIMARY_CRED_FALLBACK: str = "allow_primary_cred_fallback"

SUB_ATTR_PRIMARY: str = "primary"

OAUTH2_SCOPE_EMAIL: str = ATTR_EMAIL
OAUTH2_SCOPE_GROUPS: str = "groups"
OAUTH2_SCOPE_SSH_PUBLICKEYS: str = "ssh_publickeys"
OAUTH2_SCOPE_OPENID: str = "openid"
OAUTH2_SCOPE_READ: str = "read"
OAUTH2_SCOPE_SUPPLEMENT: str = "supplement"

LDAP_ATTR_CN: str = "cn"
LDAP_ATTR_DN: str = "dn"
LDAP_ATTR_DISPLAY_NAME: str = "displayname"
LDAP_ATTR_EMAIL_ALTERNATIVE: str = "emailalternative"
LDAP_ATTR_EMAIL_PRIMARY: str = "emailprimary"
LDAP_ATTR_ENTRYDN: str = "entrydn"
LDAP_ATTR_ENTRYUUID: str = "entryuuid"
LDAP_ATTR_GROUPS: str = "groups"
LDAP_ATTR_KEYS: str = "keys"
LDAP_ATTR_MAIL_ALTERNATIVE: str = "mailalternative"
LDAP_ATTR_MAIL_PRIMARY: str = "mailprimary"
LDAP_ATTR_MAIL: str = "mail"
LDAP_ATTR_MEMBER: str = "member"
LDAP_ATTR_NAME: str = "name"
LDAP_ATTR_OBJECTCLASS: str = "objectclass"
LDAP_ATTR_OU: str = "ou"
LDAP_ATTR_UID: str = "uid"
LDAP_CLASS_GROUPOFNAMES: str = "groupofnames"

# Rust can't deal with this being compiled out, don't try and #[cfg()] them
TEST_ATTR_NON_EXIST: str = "non-exist"
TEST_ATTR_TEST_ATTR: str = "testattr"
TEST_ATTR_EXTRA: str = "extra"
TEST_ATTR_NUMBER: str = "testattrnumber"
TEST_ATTR_NOTALLOWED: str = "notallowed"
TEST_ENTRYCLASS_TEST_CLASS: str = "testclass"

## HTTP Header containing an auth session ID for when you're going through an auth flow
KSESSIONID: str = "X-KANIDM-AUTH-SESSION-ID"
## HTTP Header containing the backend operation ID
KOPID: str = "X-KANIDM-OPID"
## HTTP Header containing the Kanidm server version
KVERSION: str = "X-KANIDM-VERSION"

## X-Forwarded-For header
X_FORWARDED_FOR: str = "x-forwarded-for"

# OAuth
OAUTH2_DEVICE_CODE_SESSION: str = "oauth2_device_code_session"
OAUTH2_RESOURCE_SERVER: str = "oauth2_resource_server"
OAUTH2_RESOURCE_SERVER_BASIC: str = "oauth2_resource_server_basic"
OAUTH2_RESOURCE_SERVER_PUBLIC: str = "oauth2_resource_server_public"

# Access Control
ACCESS_CONTROL_CREATE: str = "access_control_create"
ACCESS_CONTROL_DELETE: str = "access_control_delete"
ACCESS_CONTROL_MODIFY: str = "access_control_modify"
ACCESS_CONTROL_PROFILE: str = "access_control_profile"
ACCESS_CONTROL_RECEIVER_ENTRY_MANAGER: str = "access_control_receiver_entry_manager"
ACCESS_CONTROL_RECEIVER_GROUP: str = "access_control_receiver_group"
ACCESS_CONTROL_SEARCH: str = "access_control_search"
ACCESS_CONTROL_TARGET_SCOPE: str = "access_control_target_scope"

## Entryclass
ENTRYCLASS_BUILTIN: str = "builtin"
ENTRYCLASS_ACCOUNT: str = "account"
ENTRYCLASS_ACCOUNT_POLICY: str = "account_policy"
ENTRYCLASS_APPLICATION: str = "application"
ENTRYCLASS_ATTRIBUTE_TYPE: str = "attributetype"
ENTRYCLASS_CLASS: str = "class"
ENTRYCLASS_CLASS_TYPE: str = "classtype"
ENTRYCLASS_CLIENT_CERTIFICATE: str = "client_certificate"
ENTRYCLASS_CONFLICT: str = "conflict"
ENTRYCLASS_DOMAIN_INFO: str = "domain_info"
ENTRYCLASS_DYN_GROUP: str = "dyngroup"
ENTRYCLASS_EXTENSIBLE_OBJECT: str = "extensibleobject"
ENTRYCLASS_GROUP: str = "group"
ENTRYCLASS_MEMBER_OF: str = "memberof"
ENTRYCLASS_OBJECT: str = "object"
ENTRYCLASS_ORG_PERSON: str = "orgperson"
ENTRYCLASS_PERSON: str = "person"
ENTRYCLASS_POSIX_ACCOUNT: str = "posixaccount"
ENTRYCLASS_POSIX_GROUP: str = "posixgroup"
ENTRYCLASS_RECYCLED: str = "recycled"
ENTRYCLASS_SERVICE: str = "service"
ENTRYCLASS_SERVICE_ACCOUNT: str = "service_account"
ENTRYCLASS_SYNC_ACCOUNT: str = "sync_account"
ENTRYCLASS_SYNC_OBJECT: str = "sync_object"
ENTRYCLASS_SYSTEM: str = "system"
ENTRYCLASS_SYSTEM_CONFIG: str = "system_config"
ENTRYCLASS_SYSTEM_INFO: str = "system_info"
ENTRYCLASS_TOMBSTONE: str = "tombstone"
ENTRYCLASS_USER: str = "user"
ENTRYCLASS_KEY_PROVIDER: str = "key_provider"
ENTRYCLASS_KEY_PROVIDER_INTERNAL: str = "key_provider_internal"
ENTRYCLASS_KEY_OBJECT: str = "key_object"
ENTRYCLASS_KEY_OBJECT_JWT_ES256: str = "key_object_jwt_es256"
ENTRYCLASS_KEY_OBJECT_JWE_A128GCM: str = "key_object_jwe_a128gcm"
ENTRYCLASS_KEY_OBJECT_INTERNAL: str = "key_object_internal"
