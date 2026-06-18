
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

class AgentOSError(Exception):
    """Base class for all agent-os exceptions."""
    pass

class SecurityError(AgentOSError):
    """Raised when a security policy is violated."""
    pass

class GovernanceDenied(SecurityError):
    """Raised when a governance gate denies execution."""
    pass

class AdapterNotFoundError(AgentOSError):
    """Raised when an integration adapter is not found."""
    pass

class AdapterTimeoutError(AgentOSError):
    """Raised when an adapter operation times out."""
    pass

class ConfigurationError(AgentOSError):
    """Raised when configuration is invalid."""
    pass

class PolicyEvaluationError(AgentOSError):
    """Raised when policy evaluation fails."""
    pass

class PolicyNotFoundError(AgentOSError):
    """Raised when a referenced policy file is missing."""
    pass

class InvalidPolicyError(AgentOSError):
    """Raised when policy syntax or structure is invalid."""
    pass

class IdentityError(AgentOSError):
    """Raised for identity-related failures."""
    pass

class DelegationError(AgentOSError):
    """Raised for delegation chain issues."""
    pass

class EvidenceError(AgentOSError):
    """Raised when evidence is missing or invalid."""
    pass

class GovernanceTier(AgentOSError):
    """Raised for governance tier violations."""
    pass

class TimeoutError(AgentOSError):
    """Raised when an operation times out."""
    pass

class RetryableError(AgentOSError):
    """Raised for errors that may be retried."""
    pass

class InvalidStateError(AgentOSError):
    """Raised when the system is in an invalid state."""
    pass

class IntegrityError(AgentOSError):
    """Raised for integrity check failures."""
    pass

class AuditError(AgentOSError):
    """Raised for audit logging failures."""
    pass

class BudgetError(AgentOSError):
    """Raised when a budget (e.g., token or cost limit) is exceeded."""
    pass

class QuotaExceededError(AgentOSError):
    """Raised when a quota is exceeded."""
    pass

class RateLimitError(AgentOSError):
    """Raised when a rate limit is hit."""
    pass

class DependencyError(AgentOSError):
    """Raised for missing or misconfigured dependencies."""
    pass

class VersionError(AgentOSError):
    """Raised for version incompatibilities."""
    pass

class SerializationError(AgentOSError):
    """Raised for serialisation/deserialisation errors."""
    pass

class CryptographicError(AgentOSError):
    """Raised for cryptographic operation failures."""
    pass

class AttestationError(AgentOSError):
    """Raised for attestation failures."""
    pass

class EvidenceFreshnessError(AgentOSError):
    """Raised when evidence is stale."""
    pass
class BudgetExceededError(AgentOSError):
    """Raised when a budget is exceeded."""
    pass
class BudgetWarningError(AgentOSError):
    """Raised when a budget warning threshold is exceeded."""
    pass
class BudgetError(AgentOSError):
    pass

class BudgetExceededError(AgentOSError):
    pass

class BudgetWarningError(AgentOSError):
    pass

class CredentialExpiredError(AgentOSError):
    pass

class CredentialNotFoundError(AgentOSError):
    pass

class PermissionDeniedError(AgentOSError):
    pass

class ResourceExhaustedError(AgentOSError):
    pass

class NotInitializedError(AgentOSError):
    pass

class AlreadyExistsError(AgentOSError):
    pass

class NotFoundError(AgentOSError):
    pass

class ValidationError(AgentOSError):
    pass

class UnsupportedError(AgentOSError):
    pass

class InternalError(AgentOSError):
    pass
class IdentityVerificationError(AgentOSError):
    pass
class IntegrationError(AgentOSError):
    pass
class MissingConfigError(AgentOSError):
    pass
class PolicyDeniedError(AgentOSError):
    pass
class PolicyError(AgentOSError):
    pass
class PolicyTimeoutError(AgentOSError):
    pass
class PolicyViolationError(AgentOSError):
    pass
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

class AgentOSError(Exception):
    pass

class SecurityError(AgentOSError):
    pass

class GovernanceDenied(SecurityError):
    pass

class AdapterNotFoundError(AgentOSError):
    pass

class AdapterTimeoutError(AgentOSError):
    pass

class ConfigurationError(AgentOSError):
    pass

class PolicyEvaluationError(AgentOSError):
    pass

class PolicyNotFoundError(AgentOSError):
    pass

class InvalidPolicyError(AgentOSError):
    pass

class IdentityError(AgentOSError):
    pass

class DelegationError(AgentOSError):
    pass

class EvidenceError(AgentOSError):
    pass

class GovernanceTier(AgentOSError):
    pass

class TimeoutError(AgentOSError):
    pass

class RetryableError(AgentOSError):
    pass

class InvalidStateError(AgentOSError):
    pass

class IntegrityError(AgentOSError):
    pass

class AuditError(AgentOSError):
    pass

class BudgetError(AgentOSError):
    pass

class BudgetExceededError(AgentOSError):
    pass

class BudgetWarningError(AgentOSError):
    pass

class CredentialExpiredError(AgentOSError):
    pass

class CredentialNotFoundError(AgentOSError):
    pass

class PermissionDeniedError(AgentOSError):
    pass

class ResourceExhaustedError(AgentOSError):
    pass

class NotInitializedError(AgentOSError):
    pass

class AlreadyExistsError(AgentOSError):
    pass

class NotFoundError(AgentOSError):
    pass

class ValidationError(AgentOSError):
    pass

class UnsupportedError(AgentOSError):
    pass

class InternalError(AgentOSError):
    pass