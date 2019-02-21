import base64
import binascii


def decode_message(queue_message):
    try:
        msg = base64.b64decode(queue_message.content).decode('utf-8')
    except binascii.Error:
        msg = queue_message.content
    return msg


def encode_message(dictionary):
    try:
        # ensure bytes
        dictionary = order.encode('utf-8')
    except AttributeError:
        pass
    return base64.b64encode(dictionary).decode('utf-8')
