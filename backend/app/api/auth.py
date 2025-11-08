"""Authentication API endpoints."""

from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, ValidationError, validate
from app import db, limiter
from app.models.user import User
from app.core.security import hash_password, verify_password, log_security_event
import subprocess
import json as json_lib
from datetime import datetime


class RegisterSchema(Schema):
    """Schema for user registration."""

    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    role = fields.Str(validate=validate.OneOf(["Admin", "Developer"]))


class LoginSchema(Schema):
    """Schema for user login."""

    username = fields.Str(required=True)
    password = fields.Str(required=True)


class Register(Resource):
    """User registration endpoint."""

    @limiter.limit("5 per minute")
    def post(self):
        """Register a new user."""
        schema = RegisterSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        # Check if user exists
        if User.query.filter_by(username=data["username"]).first():
            return {"error": "Username already exists"}, 400

        if User.query.filter_by(email=data["email"]).first():
            return {"error": "Email already exists"}, 400

        # Create user
        user = User(
            username=data["username"],
            email=data["email"],
            password_hash=hash_password(data["password"]),
            role=data.get("role", "Developer"),
        )

        db.session.add(user)
        db.session.commit()

        log_security_event("user_registered", user.id)

        return {"message": "User registered successfully", "user": user.to_dict()}, 201


class Login(Resource):
    """User login endpoint."""

    @limiter.limit("10 per minute")
    def post(self):
        """Login user."""
        schema = LoginSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        user = User.query.filter_by(username=data["username"]).first()

        if not user or not user.password_hash or not verify_password(data["password"], user.password_hash):
            log_security_event("login_failed", None, {"username": data["username"]})
            return {"error": "Invalid credentials"}, 401

        if not user.is_active:
            return {"error": "Account is disabled"}, 403

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        log_security_event("login_success", user.id)

        return {"access_token": access_token, "refresh_token": refresh_token, "user": user.to_dict()}, 200


class GitHubAuth(Resource):
    """GitHub OAuth initiation endpoint."""

    def get(self):
        """Redirect to GitHub OAuth."""
        from flask import current_app

        github_client_id = current_app.config["GITHUB_CLIENT_ID"]
        redirect_uri = current_app.config["GITHUB_CALLBACK_URL"]

        github_auth_url = (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={github_client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=user:email"
        )

        return {"auth_url": github_auth_url}, 200


class GitHubCallback(Resource):
    """GitHub OAuth callback endpoint."""

    @limiter.limit("10 per minute")
    def get(self):
        """Handle GitHub OAuth callback."""
        from flask import current_app

        code = request.args.get("code")
        if not code:
            return {"error": "Authorization code not provided"}, 400

        # Exchange code for access token using curl to bypass eventlet DNS issues
        github_client_id = current_app.config["GITHUB_CLIENT_ID"]
        github_client_secret = current_app.config["GITHUB_CLIENT_SECRET"]

        try:
            # Use curl via subprocess to bypass Python's socket module entirely
            curl_cmd = [
                "curl",
                "-s",
                "-X",
                "POST",
                "https://github.com/login/oauth/access_token",
                "-H",
                "Accept: application/json",
                "-d",
                f"client_id={github_client_id}",
                "-d",
                f"client_secret={github_client_secret}",
                "-d",
                f"code={code}",
                "--connect-timeout",
                "30",
                "--max-time",
                "30",
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=35)

            if result.returncode != 0:
                current_app.logger.error(f"Curl failed: {result.stderr}")
                error_msg = "Failed to connect to GitHub. " "Please check your internet connection and DNS settings."
                return {"error": error_msg}, 503

            try:
                token_data = json_lib.loads(result.stdout)
            except json_lib.JSONDecodeError:
                current_app.logger.error(f"Invalid JSON response: {result.stdout}")
                return {"error": "Invalid response from GitHub"}, 500

        except subprocess.TimeoutExpired:
            current_app.logger.error("GitHub OAuth request timed out")
            return {"error": "Request to GitHub timed out. Please try again."}, 504
        except Exception as e:
            current_app.logger.error(f"GitHub OAuth error: {e}")
            return {"error": f"An error occurred during GitHub authentication: {str(e)}"}, 500

        # Check for error in response
        if "error" in token_data:
            error_desc = token_data.get("error_description", token_data.get("error"))
            current_app.logger.error(f"GitHub OAuth error: {error_desc}")
            return {"error": f"GitHub OAuth failed: {error_desc}"}, 400

        access_token = token_data.get("access_token")

        if not access_token:
            return {"error": "Failed to get access token"}, 400

        # Get user info from GitHub using curl
        try:
            curl_cmd = [
                "curl",
                "-s",
                "https://api.github.com/user",
                "-H",
                f"Authorization: token {access_token}",
                "--connect-timeout",
                "30",
                "--max-time",
                "30",
            ]

            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=35)

            if result.returncode != 0:
                current_app.logger.error(f"Curl failed: {result.stderr}")
                error_msg = (
                    "Failed to connect to GitHub API. " "Please check your internet connection and DNS settings."
                )
                return {"error": error_msg}, 503

            try:
                github_user = json_lib.loads(result.stdout)
            except json_lib.JSONDecodeError:
                current_app.logger.error(f"Invalid JSON response: {result.stdout}")
                return {"error": "Invalid response from GitHub API"}, 500

        except subprocess.TimeoutExpired:
            current_app.logger.error("GitHub API request timed out")
            return {"error": "Request to GitHub API timed out. Please try again."}, 504
        except Exception as e:
            current_app.logger.error(f"GitHub API error: {e}")
            error_msg = "An error occurred while fetching user info from GitHub"
            return {"error": f"{error_msg}: {str(e)}"}, 500

        # Check if we got valid user data
        if "id" not in github_user:
            current_app.logger.error(f"Invalid user data from GitHub: {github_user}")
            return {"error": "Failed to get user info from GitHub"}, 400

        github_id = str(github_user["id"])
        username = github_user["login"]
        email = github_user.get("email")

        # Get email if not in user info using curl
        if not email:
            try:
                curl_cmd = [
                    "curl",
                    "-s",
                    "https://api.github.com/user/emails",
                    "-H",
                    f"Authorization: token {access_token}",
                    "--connect-timeout",
                    "30",
                    "--max-time",
                    "30",
                ]

                result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=35)

                if result.returncode == 0:
                    try:
                        emails = json_lib.loads(result.stdout)
                        email = next((e["email"] for e in emails if e["primary"]), None)
                    except json_lib.JSONDecodeError:
                        current_app.logger.warning("Failed to parse email response from GitHub")
            except Exception as e:
                current_app.logger.warning(f"Failed to fetch email from GitHub: {e}")
                # Continue without email - will use fallback

        # Find or create user
        user = User.query.filter_by(github_id=github_id).first()

        if not user:
            # Check if email already exists
            if email:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    return {"error": "Email already registered"}, 400

            user = User(
                username=username, email=email or f"{username}@github.local", github_id=github_id, role="Developer"
            )
            db.session.add(user)
            db.session.commit()
            log_security_event("user_registered_github", user.id)
        else:
            user.last_login = datetime.utcnow()
            db.session.commit()

        # Create tokens
        access_token_jwt = create_access_token(identity=user.id)
        refresh_token_jwt = create_refresh_token(identity=user.id)

        log_security_event("login_success_github", user.id)

        return {"access_token": access_token_jwt, "refresh_token": refresh_token_jwt, "user": user.to_dict()}, 200


class RefreshToken(Resource):
    """Token refresh endpoint."""

    @jwt_required(refresh=True)
    def post(self):
        """Refresh access token."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.is_active:
            return {"error": "User not found or inactive"}, 404

        new_token = create_access_token(identity=user_id)
        return {"access_token": new_token}, 200


class Logout(Resource):
    """Logout endpoint."""

    @jwt_required()
    def post(self):
        """Logout user."""
        get_jwt()["jti"]  # Get JTI for potential blacklist
        # In production, add jti to blacklist
        log_security_event("logout", get_jwt_identity())
        return {"message": "Logged out successfully"}, 200


class UserProfile(Resource):
    """User profile endpoint."""

    @jwt_required()
    def get(self):
        """Get user profile."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return {"error": "User not found"}, 404

        return {"user": user.to_dict()}, 200
