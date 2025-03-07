from __future__ import absolute_import, annotations, division, print_function

from ..arg_specs.oauth import KanidmOauthArgs
from ..arg_specs.oauth_sub import PrefUsername
from ..exceptions import (
    KanidmAuthenticationFailure,
    KanidmModuleError,
    KanidmRequiredOptionError,
    KanidmArgsException,
)
from .api import KanidmApi
from .attrs import (
    ATTR_DISPLAYNAME,
    ATTR_NAME,
    ATTR_OAUTH2_ALLOW_INSECURE_CLIENT_DISABLE_PKCE,
    ATTR_OAUTH2_ALLOW_LOCALHOST_REDIRECT,
    ATTR_OAUTH2_JWT_LEGACY_CRYPTO_ENABLE,
    ATTR_OAUTH2_PREFER_SHORT_USERNAME,
    ATTR_OAUTH2_RS_ORIGIN,
    ATTR_OAUTH2_RS_ORIGIN_LANDING,
    ATTR_OAUTH2_STRICT_REDIRECT_URI,
    ATTR_UUID,
)
import traceback
from ansible.module_utils.compat.typing import (
    Optional,
)

REQUESTS_TOOLS_IMP_ERR = None
try:
    from requests_toolbelt.multipart.encoder import MultipartEncoder, FileWrapper

    HAS_REQUESTS_TOOLS = True
except ImportError:
    REQUESTS_TOOLS_IMP_ERR = traceback.format_exc()
    HAS_REQUESTS_TOOLS = False


class KanidmOAuth(object):
    def __init__(self, args: KanidmOauthArgs):
        self.args: KanidmOauthArgs = args
        self.api = KanidmApi(args=args.kanidm, debug=args.debug)

    def create_oauth_client(self) -> str:
        self.api.authenticate()

        if not self.api.check_token():
            raise KanidmAuthenticationFailure(
                "Unable to establish an authenticated connection with the kanidm server"
            )

        if not self.get_client():
            if not self.args.public:
                if not self.create_basic_client():
                    raise KanidmModuleError(
                        f"Unable to create or get client {self.args.name}. Got {self.api.error}"
                    )
            else:
                if not self.create_public_client():
                    raise KanidmModuleError(
                        f"Unable to create or get public client {self.args.name}. Got {self.api.error}"
                    )

        if not self.get_client():
            raise KanidmModuleError(
                f"Unable to get client {self.args.name}. Got {self.api.error}"
            )

        if not self.args.public:
            if not self.set_pkce():
                raise KanidmModuleError(
                    f"Unable to set PKCE for client {self.args.name}. Got {self.api.error}"
                )

            if not self.set_legacy_crypto():
                raise KanidmModuleError(
                    f"Unable to set legacy crypto for client {self.args.name}. Got {self.api.error}"
                )
        else:
            if not self.set_localhost_redirect():
                raise KanidmModuleError(
                    f"Unable to set localhost redirect policy for client {self.args.name}. Got {self.api.error}"
                )

        if not self.add_redirect_urls():
            raise KanidmModuleError(
                f"Unable to add redirect URLs for client {self.args.name}. Got {self.api.error}"
            )

        if not self.update_scope_map():
            raise KanidmModuleError(
                f"Unable to update scope map for client {self.args.name}. Got {self.api.error}"
            )

        if not self.set_preferred_username():
            raise KanidmModuleError(
                f"Unable to set preferred username for client {self.args.name}. Got {self.api.error}"
            )

        if not self.set_strict_redirect():
            raise KanidmModuleError(
                f"Unable to set strict redirect for client {self.args.name}. Got {self.api.error}"
            )

        if self.args.image is not None:
            if not self.add_image():
                raise KanidmModuleError(
                    f"Unable to add image for client {self.args.name}. Got {self.api.error}"
                )

        if self.args.sup_scopes is not None:
            if not self.update_sup_scope_map():
                raise KanidmModuleError(
                    f"Unable to update supplemental scope map for client {self.args.name}. Got {self.api.error}"
                )

        if self.args.custom_claims is not None:
            if not self.update_custom_claim_map():
                raise KanidmModuleError(
                    f"Unable to update custom claim map for client {self.args.name}. Got {self.api.error}"
                )

            if not self.update_custom_claim_join():
                raise KanidmModuleError(
                    f"Unable to update custom claim join for client {self.args.name}. Got {self.api.error}"
                )

        if not self.get_client_secret():
            raise KanidmModuleError(
                f"Unable to get client secret for client {self.args.name}. Got {self.api.error}"
            )

        if self.api.text is None:
            raise KanidmModuleError(
                f"Unable to parse the client secret for client {self.args.name}. Got {self.api.text}"
            )

        return self.api.text

    def get_client(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        if not self.api.get(
            name="get_client",
            path=f"/v1/oauth2/{self.args.name}",
        ):
            return False

        try:
            self.api.text = self.api.json["attrs"][ATTR_UUID]
        except Exception:
            self.api.text = ""
            return False

        return True

    def create_basic_client(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.url is None:
            raise KanidmRequiredOptionError("No url specified")

        return self.api.post(
            name="create_basic_client",
            path="/v1/oauth2/_basic",
            json={
                "attrs": {
                    ATTR_NAME: [self.args.name],
                    ATTR_DISPLAYNAME: [self.args.display_name],
                    ATTR_OAUTH2_RS_ORIGIN_LANDING: [self.args.url],
                    ATTR_OAUTH2_STRICT_REDIRECT_URI: [
                        str(self.args.strict_redirect).lower()
                    ],
                }
            },
        )

    def create_public_client(self) -> bool:
        if not self.args.public:
            raise KanidmArgsException(
                "Unable to create a public client when public is not specified"
            )
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.url is None:
            raise KanidmRequiredOptionError("No url specified")

        return self.api.post(
            name="create_public_client",
            path="/v1/oauth2/_public",
            json={
                "attrs": {
                    ATTR_NAME: [self.args.name],
                    ATTR_DISPLAYNAME: [self.args.display_name],
                    ATTR_OAUTH2_RS_ORIGIN_LANDING: [self.args.url],
                    ATTR_OAUTH2_STRICT_REDIRECT_URI: [
                        str(self.args.strict_redirect).lower()
                    ],
                }
            },
        )

    def update_scope_map(self) -> bool:
        if not self.args.group:
            raise KanidmRequiredOptionError("No group specified")
        if not self.args.name:
            raise KanidmRequiredOptionError("No name specified")
        if not self.args.scopes:
            raise KanidmRequiredOptionError("No scopes specified")

        return self.api.post(
            name="update_scope_map",
            path=f"/v1/oauth2/{self.args.name}/_scopemap/{self.args.group}",
            json=self.args.scopes,
        )

    def update_sup_scope_map(self, index: Optional[int] = None) -> bool:
        if not self.args.sup_scopes:
            raise KanidmRequiredOptionError("No supplemental scopes specified")
        if not self.args.name:
            raise KanidmRequiredOptionError("No name specified")

        if index is not None:
            return self.api.post(
                name=f"update_sup_scope_map[{index}]",
                path=f"/v1/oauth2/{self.args.name}/_sup_scopemap/{self.args.sup_scopes[index].group}",
                json=self.args.sup_scopes[index].scopes,
            )

        else:
            for i, sup_scope in enumerate(self.args.sup_scopes):
                if not self.api.post(
                    name=f"update_sup_scope_map[{i}]",
                    path=f"/v1/oauth2/{self.args.name}/_sup_scopemap/{sup_scope.group}",
                    json=sup_scope.scopes,
                ):
                    return False

        return self.api.verify_response()

    def add_image(self) -> bool:
        if self.args.image is None:
            raise KanidmRequiredOptionError("No image specified")
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        self.args.image.get()

        m = MultipartEncoder(
            {
                "image": (
                    f"{self.args.name}.{self.args.image.format.value}",
                    FileWrapper(open(self.args.image.src, "rb")),
                    self.args.image.format.mime(),
                )
            }
        )

        if not self.api.post(
            name="add_image",
            path=f"/v1/oauth2/{self.args.name}/_image",
            data=m,
            content_type=m.content_type,
        ):
            return False

        return True

    def set_pkce(self) -> bool:
        if self.args.pkce is None:
            raise KanidmRequiredOptionError("No PKCE specified")

        return self.api.patch_oauth(
            name="set_pkce",
            oauth_name=self.args.name,
            attrs={
                ATTR_OAUTH2_ALLOW_INSECURE_CLIENT_DISABLE_PKCE: [
                    str(self.args.pkce).lower()
                ],
            },
        )

    def set_legacy_crypto(self) -> bool:
        if self.args.legacy_crypto is None:
            raise KanidmRequiredOptionError("No legacy crypto specified")

        return self.api.patch_oauth(
            name="set_legacy_crypto",
            oauth_name=self.args.name,
            attrs={
                ATTR_OAUTH2_JWT_LEGACY_CRYPTO_ENABLE: [
                    str(self.args.legacy_crypto).lower()
                ],
            },
        )

    def set_preferred_username(self) -> bool:
        if self.args.username is None:
            raise KanidmRequiredOptionError("No username specified")

        return self.api.patch_oauth(
            name="set_preferred_username",
            oauth_name=self.args.name,
            attrs={
                ATTR_OAUTH2_PREFER_SHORT_USERNAME: [
                    str(self.args.username == PrefUsername.short).lower()
                ],
            },
        )

    def set_localhost_redirect(self) -> bool:
        if self.args.local_redirect is None:
            raise KanidmRequiredOptionError("No localhost redirect specified")

        return self.api.patch_oauth(
            name="set_localhost_redirect",
            oauth_name=self.args.name,
            attrs={
                ATTR_OAUTH2_ALLOW_LOCALHOST_REDIRECT: [
                    str(self.args.local_redirect).lower()
                ]
            },
        )

    def set_strict_redirect(self) -> bool:
        if self.args.strict_redirect is None:
            raise KanidmRequiredOptionError("No strict redirect specified")

        return self.api.patch_oauth(
            name="set_strict_redirect",
            oauth_name=self.args.name,
            attrs={
                ATTR_OAUTH2_STRICT_REDIRECT_URI: [
                    str(self.args.strict_redirect).lower()
                ],
            },
        )

    def update_custom_claim_map(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.custom_claims is None:
            raise KanidmRequiredOptionError("No claims specified")
        if self.args.group is None:
            raise KanidmRequiredOptionError("No group specified")

        for i, c in enumerate(self.args.custom_claims):
            if not self.api.post(
                name=f"update_custom_claim_map[{i}]",
                path=f"/v1/oauth2/{self.args.name}/_claimmap/{self.args.name}/{self.args.group}",
                json=[str(v) for v in c.values],
            ):
                return False
        return True

    def update_custom_claim_join(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.claim_join is None:
            raise KanidmRequiredOptionError("No claim join specified")
        if self.args.custom_claims is None:
            raise KanidmRequiredOptionError("No claims specified")

        for i, c in enumerate(self.args.custom_claims):
            if not self.api.post(
                name=f"update_custom_claim_join[{i}]",
                path=f"/v1/oauth2/{self.args.name}/_claimmap/{self.args.claim_join}",
                json=self.args.claim_join,
            ):
                return False

        return True

    def add_redirect_urls(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")
        if self.args.redirect_url is None:
            raise KanidmRequiredOptionError("No redirect URL specified")

        for url in self.args.redirect_url:
            if not self.api.patch_oauth(
                name=f"add_redirect_url[{url}]",
                oauth_name=self.args.name,
                attrs={ATTR_OAUTH2_RS_ORIGIN: [url]},
            ):
                return False
        return True

    def get_client_secret(self) -> bool:
        if self.args.name is None:
            raise KanidmRequiredOptionError("No name specified")

        return self.api.get(
            name="get_client_secret",
            path=f"/v1/oauth2/{self.args.name}/_basic_secret",
        )
