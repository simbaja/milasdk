from datetime import datetime
from typing import Any, Dict, Optional

from graphql import GraphQLScalarType, ValueNode
from graphql.utilities import value_from_ast_untyped

# Date: An ISO-8601 encoded date string in format "yyyy-MM-dd". For instance, "2021-04-12".

def serialize_date(value: Any) -> str:
    return value.date.isoformat()

def parse_date_value(value: Any) -> datetime:
    return datetime.fromisoformat(value)

def parse_date_literal(
    value_node: ValueNode, variables: Optional[Dict[str, Any]] = None
) -> datetime:
    ast_value = value_from_ast_untyped(value_node, variables)
    return parse_date_value(ast_value)

DateScalar = GraphQLScalarType(
    name="Date",
    serialize=serialize_date,
    parse_value=parse_date_value,
    parse_literal=parse_date_literal,
)

# EpochSecond: The unix time stamp. The number of seconds between a particular instant and the Unix Epoch of 1970-01-01T00:00:00Z.

def serialize_epoch(value: Any) -> str:
    return int(round(value.timestamp()))

def parse_epoch_value(value: Any) -> datetime:
    return datetime.fromtimestamp(value)

def parse_epoch_literal(
    value_node: ValueNode, variables: Optional[Dict[str, Any]] = None
) -> datetime:
    ast_value = value_from_ast_untyped(value_node, variables)
    return parse_epoch_value(ast_value)

EpochSecondScalar = GraphQLScalarType(
    name="Date",
    serialize=serialize_epoch,
    parse_value=parse_epoch_value,
    parse_literal=parse_epoch_literal,
)