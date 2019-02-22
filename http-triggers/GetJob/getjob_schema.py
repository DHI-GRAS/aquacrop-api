from marshmallow import Schema, fields, validate


class GetJobSchema(Schema):
    num_messages = fields.Int(required=True)
