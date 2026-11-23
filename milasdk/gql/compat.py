"""gql version detection.

gql 3.5 already exports GraphQLRequest, but only gql 4 passes one to
transports and requires it in AsyncClientSession.execute(), so the major
version (not the presence of the class) decides which calling convention
to use.
"""

import gql

GQL_V4: bool = int(gql.__version__.split(".")[0]) >= 4
