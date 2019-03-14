from marshmallow import Schema, fields, validate


AREA_TYPES = []
QUERY_RESPONSE_STATUS = ['awaiting', 'completed', 'failed']


class GeometrySchema(Schema):
    coordinates = fields.List(fields.List(fields.List(fields.Float)))
    type = fields.String(validate.OneOf(['Polygon']))


class SubmitMessageSchema(Schema):
    area_name = fields.String(required=True)
    crop = fields.String(required=True)
    planting_date = fields.Date(format="%Y-%m-%d")
    irrigated = fields.Boolean(required=True)
    fraction = fields.Float(required=True)
    geometry = fields.Nested(GeometrySchema)


class AwaitSchema(Schema):
    guid = fields.UUID(required=True)
    area_name = fields.String(required=True)
    crop = fields.String(required=True)
    planting_date = fields.Date(format="%Y-%m-%d")
    irrigated = fields.Boolean(required=True)
    fraction = fields.Float(required=True)
    geometry = fields.Nested(GeometrySchema)


class DoneSchema(Schema):
    guid = fields.UUID(required=True)
    error = fields.String(required=True, allow_none=True)


class SubmitResponseSchema(Schema):
    guid = fields.UUID(required=True)


class QueryResponseSchema(Schema):
    status = fields.String(validate.OneOf(QUERY_RESPONSE_STATUS))
    error = fields.String(required=True, allow_none=True)
