import enum


class Gender(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class RelationshipType(str, enum.Enum):
    PARENT_OF = "PARENT_OF"
    SPOUSE_OF = "SPOUSE_OF"
    SIBLING_OF = "SIBLING_OF"


class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
