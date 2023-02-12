import datetime
import uuid
from unittest import TestCase
from unittest import mock

import jwt

from app.auth.tokens import Token, AccessToken, RefreshToken
from app.config import settings


class TokenSecurityTests(TestCase):
    def test_jwt_token_no_algorithm_exception(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        dt = now + datetime.timedelta(minutes=1)
        token = jwt.encode({
            'uid': 1,
            'exp': dt.timestamp(),
            'iat': now.timestamp(),
            'jti': uuid.uuid4().hex,
            'issuer': 'test'
        }, None, algorithm='none')

        with self.assertRaises(jwt.exceptions.InvalidAlgorithmError):
            Token.decode_token(token, issuer='test')

    def test_jwt_token_no_claims_exception(self):
        token = jwt.encode({
            'uid': 1
        }, settings.SECRET_KEY, algorithm='HS256')

        with self.assertRaises(jwt.exceptions.MissingRequiredClaimError):
            Token.decode_token(token, issuer='test')

    def test_jwt_token_wrong_algorithm_exception(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        dt = now + datetime.timedelta(minutes=1)
        token = jwt.encode({
            'uid': 1,
            'exp': dt.timestamp(),
            'iat': now.timestamp(),
            'jti': uuid.uuid4().hex,
            'iss': 'test'
        }, settings.SECRET_KEY, algorithm='HS512')

        with self.assertRaises(jwt.exceptions.InvalidAlgorithmError):
            Token.decode_token(token, issuer='test')

    def test_jwt_token_expired_exception(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        issued = now - datetime.timedelta(minutes=2)
        dt = now - datetime.timedelta(minutes=1)
        token = jwt.encode({
            'uid': 1,
            'exp': dt.timestamp(),
            'iat': issued.timestamp(),
            'jti': uuid.uuid4().hex,
            'iss': 'test'
        }, settings.SECRET_KEY, algorithm='HS256')

        with self.assertRaises(jwt.exceptions.ExpiredSignatureError):
            Token.decode_token(token, issuer='test')

    def test_jwt_wrong_token_exception(self):
        with self.assertRaises(jwt.exceptions.DecodeError):
            Token.decode_token('wrong token', issuer='test')

    def test_jwt_proper_token(self):
        now = datetime.datetime.now()
        issued = now - datetime.timedelta(minutes=1)
        dt = now + datetime.timedelta(minutes=2)
        token = jwt.encode({
            'uid': 1,
            'exp': dt.timestamp(),
            'iat': issued.timestamp(),
            'jti': uuid.uuid4().hex,
            'iss': 'test'
        }, settings.SECRET_KEY, algorithm='HS256')

        self.assertNotEqual(Token.decode_token(token, issuer='test'), None)

    def test_jwt_proper_user_id(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        issued = now - datetime.timedelta(minutes=1)
        dt = now + datetime.timedelta(minutes=1)
        user_id = 1
        token = jwt.encode({
            'uid': user_id,
            'exp': dt.timestamp(),
            'iat': issued.timestamp(),
            'jti': uuid.uuid4().hex,
            'iss': 'test'
        }, settings.SECRET_KEY, algorithm='HS256')

        decoded = Token.decode_token(token, issuer='test')
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded['uid'], user_id)

    @mock.patch('app.auth.tokens.datetime')
    def test_jwt_access_proper_datetime(self, mocked_dt):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        mocked_dt.datetime.now.return_value = now

        token = AccessToken.encode({'uid': 1})
        decoded = AccessToken.decode(token)

        self.assertIsNotNone(decoded)
        self.assertEqual(decoded['iat'], int(now.timestamp()))
        self.assertEqual(decoded['exp'], int((now + AccessToken.expire_time).timestamp()))

    @mock.patch('app.auth.tokens.datetime')
    def test_jwt_refresh_proper_datetime(self, mocked_dt):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        mocked_dt.datetime.now.return_value = now

        token = RefreshToken.encode({'uid': 1})
        decoded = RefreshToken.decode(token)

        self.assertIsNotNone(decoded)
        self.assertEqual(decoded['iat'], int(now.timestamp()))
        self.assertEqual(decoded['exp'], int((now + RefreshToken.expire_time).timestamp()))

    def test_jwt_refresh_proper_issuer(self):
        token = RefreshToken.encode({'uid': 1})
        decoded = RefreshToken.decode(token)

        self.assertIsNotNone(decoded)
        self.assertEqual(decoded['iss'], RefreshToken.issuer)

    def test_jwt_invalid_issuer(self):
        token = AccessToken.encode({'uid': 1})
        with self.assertRaises(jwt.exceptions.InvalidIssuerError):
            RefreshToken.decode(token)

        with self.assertRaises(jwt.exceptions.InvalidIssuerError):
            Token.decode_token(token, issuer='test')
