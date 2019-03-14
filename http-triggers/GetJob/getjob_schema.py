from marshmallow import Schema, fields


class GetJobSchema(Schema):
    num_messages = fields.Int(required=True)
