from passlib.hash import pbkdf2_sha512

from nebriosmodels import NebriOSModel, NebriOSField, NebriOSReference


class Oauth2Realm(NebriOSModel):

    name = NebriOSField(required=True)


class Oauth2User(NebriOSModel):

    username = NebriOSField(required=True)
    password = NebriOSField(required=True)

    def set_password(self, password):
        self.password = pbkdf2_sha512.encrypt(password)

    def validate_password(self, password):
        return pbkdf2_sha512.verify(password, self.password)


class Oauth2Client(NebriOSModel):

    user = NebriOSReference(Oauth2User, required=True)
    realm = NebriOSReference(Oauth2Realm, required=True)
    client_key = NebriOSField(required=True)
    client_secret = NebriOSField(required=True)
    rsa_key = NebriOSField(required=True)
    redirect_uri = NebriOSField(required=True)


class Oauth2RequestToken(NebriOSModel):

    pass